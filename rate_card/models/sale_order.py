from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.sale.models.sale_order import SALE_ORDER_STATE
import copy

SALE_ORDER_STATE_RC = [
    ('draft', "Quotation"),
    ('sent', "Quotation Sent"),
    ('sale', "Sales Order"),
    ('cancel', "Revised"),
]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection=SALE_ORDER_STATE_RC,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    region_ids = fields.Many2many(
        string='Regions',
        comodel_name='rate.region',
        relation='rate_region_sales_order_rel',
        column1='region_id',
        column2='sale_order_id',
    )

    country_ids = fields.Many2many(
        string='Countries',
        comodel_name='rate.country',
        relation='rate_country_sales_order_rel',
        column1='country_id',
        column2='sale_order_id',
        domain="[('rate_region_id', 'in', region_ids)]",
    )

    city_ids = fields.Many2many(
        string='Cities',
        comodel_name='rate.city',
        relation='rate_city_sales_order_rel',
        column1='city_id',
        column2='sale_order_id',
        domain="[('rate_country_id', 'in', country_ids)]",
    )

    sla_id = fields.Many2one(
        string='sla',
        comodel_name='project.sla',
        ondelete='cascade',
        domain="[('rate_country_id', 'in', country_ids)]",
    )

    skill_id = fields.Many2one(
        string='Skillset',
        comodel_name='project.skill',
        ondelete='cascade',
    )

    sla_ids = fields.Many2many(
        string='SLAs Type',
        comodel_name='project.sla',
        relation='project_sla_sales_order_rel',
        column1='sla_id',
        column2='sale_order_id',
    )

    service_type_id = fields.Many2one(
        string='SLA',
        comodel_name='service.type',
        ondelete='cascade',
    )

    with_sla = fields.Boolean(string='SLA Enabled', tracking=True, required=False, related="service_type_id.with_sla")

    out_of_office = fields.Boolean(
        string='Include OOH',
        required=False)
    weekend = fields.Boolean(
        string='Include Holiday',
        required=False)
    worksite_count = fields.Integer(string='WorkSite Count', compute='_compute_worksite_count')
    project_name = fields.Char(string="Project Name")
    language_ids = fields.Many2many(
        comodel_name='res.lang',
        relation='sale_order_res_lang_rel',
        column1='sale_id',
        column2='lang_id',
        string='Languages'
    )

    # Fixed Discount Amount
    discount_fixed = fields.Float(string='Fixed Discount', default=0.0, )
    discount = fields.Float(string='Disc %', default=0.0, )

    # Compute Function
    def _compute_worksite_count(self):
        for sale_order in self:
            sale_order.worksite_count = self.env['project.worksite'].search_count(
                [('id', 'in', sale_order.order_line.worksite_id.ids)])

    def clear_all_lines(self):
        for rec in self:
            rec.order_line = [(5, 0, 0)]

    def create_order_lines(self):
        for rec in self:
            # Retrieve service type
            svc_type = rec.service_type_id
            if not rec.skill_id:
                raise ValidationError(
                    'Skillset is not set while create Quotation lines. Skillset is Required.')

            # Fetch configuration settings
            config_params = self.env['ir.config_parameter'].sudo()
            holiday_uplift = float(config_params.get_param('sale.holiday_uplift', default=1))
            after_hours_uplift = float(config_params.get_param('sale.after_hours_uplift', default=1))

            holiday_rate = 1  # Initialize variable
            after_hours = 1  # Initialize variable

            # Check if SLA is applied
            if rec.sla_ids and rec.with_sla:
                # Case where no cities are selected
                if not rec.city_ids:
                    for sla in rec.sla_ids:
                        for country_id in rec.country_ids:
                            language_ids = country_id.language_ids.ids
                            project_sla_line_id = sla.project_sla_line_ids.filtered(
                                lambda l: l.country_id == country_id)
                            if project_sla_line_id:
                                name = f'{country_id.rate_region_id.name}, {country_id.name}'
                                sequence = len(rec.order_line.filtered(lambda l: l.name.split('-')[0] == name))
                                previous_worksite = rec.order_line.filtered(lambda x: x.worksite_id.name == name)
                                if len(previous_worksite) == 0:
                                    # Create WorkSite:
                                    worksite = self.env['project.worksite'].create({
                                        'name': name,
                                        'country_id': country_id.id,
                                        'region_id': country_id.rate_region_id.id,
                                        'sale_order_id': rec.id,
                                    })
                                else:
                                    worksite = self.env['project.worksite'].create({
                                        'name': name,
                                        'country_id': country_id.id,
                                        'region_id': country_id.rate_region_id.id,
                                        'sale_order_id': rec.id,
                                    })
                                    worksite.sequence = previous_worksite[0].worksite_id.sequence + '-' + str(sequence)
                                name = name + '-' + str(sequence + 1)
                                svc_desc = f'{svc_type.name} - {sla.name} - {rec.skill_id.name if rec.skill_id else ""}'
                                line_rate = project_sla_line_id.rate
                                if rec.skill_id:
                                    line_rate = self._get_uplift_rate(sla, rec.skill_id, project_sla_line_id.rate)
                                if rec.out_of_office:
                                    after_hours = after_hours_uplift
                                if rec.weekend:
                                    holiday_rate = holiday_uplift
                                # Perform the creation of the order line
                                rec.order_line.create({
                                    'order_id': rec.id,
                                    'name': name,
                                    'product_id': self.env.ref('rate_card.service_fee_product').id,
                                    'product_uom_qty': self.env.ref('rate_card.service_fee_product').uom_id.id,
                                    'price_unit': line_rate,
                                    'skill_id': rec.skill_id.id,
                                    'job_description': rec.skill_id.job_description,
                                    'svc_desc': svc_desc,
                                    'svc_line': True,
                                    'out_of_office': after_hours,
                                    'holiday': holiday_rate,
                                    'rate_region_id': country_id.rate_region_id.id,
                                    'country_id': country_id.id,
                                    'language_ids': [(6, 0, language_ids)],
                                    'svc_type_id': svc_type.id,  # Added field
                                    'sla_id': sla.id,  # Added field
                                    'worksite_id': worksite.id,
                                    'discount_fixed': rec.discount_fixed if rec.discount_fixed > 0 else 0,
                                    'discount': rec.discount if rec.discount > 0 else 0,
                                })
                            else:
                                raise ValidationError(
                                    'No Country rate defined in Project SLA. Please add country rate first in Project SLA Lines.')

                    # for country_id in rec.country_ids:
                    #     language_ids = country_id.language_ids.ids
                    #     service_type_line_id = rec.service_type_id.service_type_line_ids.filtered(
                    #         lambda l: l.rate_country_id == country_id)
                    #     if service_type_line_id:
                    #         name = f'{country_id.rate_region_id.name}, {country_id.name}'
                    #         sequence = len(rec.order_line.filtered(lambda l: l.name.split('-')[0] == name))
                    #         previous_worksite = rec.order_line.filtered(lambda x: x.worksite_id.name == name)
                    #         if len(previous_worksite) == 0:
                    #             # Create WorkSite:
                    #             worksite = self.env['project.worksite'].create({
                    #                 'name': name,
                    #                 'country_id': country_id.id,
                    #                 'region_id': country_id.rate_region_id.id,
                    #                 'sale_order_id': rec.id,
                    #             })
                    #         else:
                    #             worksite = self.env['project.worksite'].create({
                    #                 'name': name,
                    #                 'country_id': country_id.id,
                    #                 'region_id': country_id.rate_region_id.id,
                    #                 'sale_order_id': rec.id,
                    #             })
                    #             worksite.sequence = previous_worksite[0].worksite_id.sequence + '-' + str(sequence)
                    #         name = name + '-' + str(sequence + 1)
                    #         svc_desc = f'{svc_type.name} - {rec.skill_id.name if rec.skill_id else ""}'
                    #         line_rate = service_type_line_id.rate
                    #         if rec.skill_id:
                    #             line_rate = self._get_uplift_rate(svc_type, rec.skill_id, service_type_line_id.rate)
                    #         if rec.out_of_office:
                    #             after_hours = after_hours_uplift
                    #         if rec.weekend:
                    #             holiday_rate = holiday_uplift
                    #         # Perform the creation of the order line
                    #         rec.order_line.create({
                    #             'order_id': rec.id,
                    #             'name': name,
                    #             'product_id': self.env.ref('rate_card.service_fee_product').id,
                    #             'product_uom_qty': self.env.ref('rate_card.service_fee_product').uom_id.id,
                    #             'price_unit': line_rate,
                    #             'skill_id': rec.skill_id.id,
                    #             'job_description': rec.skill_id.job_description,
                    #             'svc_desc': svc_desc,
                    #             'svc_line': True,
                    #             'out_of_office': after_hours,
                    #             'holiday': holiday_rate,
                    #             'rate_region_id': country_id.rate_region_id.id,
                    #             'country_id': country_id.id,
                    #             'language_ids': [(6, 0, language_ids)],
                    #             'svc_type_id': svc_type.id,  # Added field
                    #             'sla_id': False,  # Added field
                    #             'worksite_id': worksite.id,
                    #             'discount_fixed': rec.discount_fixed if rec.discount_fixed > 0 else 0,
                    #             'discount': rec.discount if rec.discount > 0 else 0,
                    #         })
                    #     else:
                    #         raise ValidationError(
                    #             'No Country rate defined in Project Service type. Please add country rate first in Service Type Lines.')



                else:
                    # Case where cities are selected
                    for sla in rec.sla_ids:
                        for city_id in rec.city_ids:
                            language_ids = city_id.rate_country_id.language_ids.ids
                            project_sla_line_id = sla.project_sla_line_ids.filtered(
                                lambda l: l.country_id == city_id.rate_country_id)
                            if project_sla_line_id:
                                name = f'{city_id.rate_country_id.rate_region_id.name}, {city_id.rate_country_id.name}, {city_id.name}'
                                sequence = len(rec.order_line.filtered(lambda l: l.name.split('-')[0] == name))
                                previous_worksite = rec.order_line.filtered(lambda x: x.worksite_id.name == name)
                                if len(previous_worksite) == 0:
                                    # Create WorkSite:
                                    worksite = self.env['project.worksite'].create({
                                        'name': name,
                                        'city_id': city_id.id,
                                        'country_id': city_id.rate_country_id.id,
                                        'region_id': city_id.rate_country_id.rate_region_id.id,
                                        'sale_order_id': rec.id,
                                    })
                                else:
                                    worksite = self.env['project.worksite'].create({
                                        'name': name,
                                        'city_id': city_id.id,
                                        'country_id': city_id.rate_country_id.id,
                                        'region_id': city_id.rate_country_id.rate_region_id.id,
                                        'sale_order_id': rec.id,
                                    })
                                    worksite.sequence = previous_worksite[0].worksite_id.sequence + '-' + str(sequence)
                                # sequence = len(rec.order_line.filtered(lambda l: l.name.split('-')[0] == name))
                                name = name + '-' + str(sequence + 1)
                                svc_desc = f'{svc_type.name} - {sla.name} - {rec.skill_id.name if rec.skill_id else ""}'
                                line_rate = project_sla_line_id.rate

                                if rec.skill_id:
                                    line_rate = self._get_uplift_rate(sla, rec.skill_id, project_sla_line_id.rate)
                                if rec.out_of_office:
                                    after_hours = after_hours_uplift
                                if rec.weekend:
                                    holiday_rate = holiday_uplift
                                    # Perform the creation of the order line
                                rec.order_line.create({
                                    'order_id': rec.id,
                                    'name': name,
                                    'product_id': self.env.ref('rate_card.service_fee_product').id,
                                    'product_uom_qty': self.env.ref('rate_card.service_fee_product').uom_id.id,
                                    'price_unit': line_rate,
                                    'skill_id': rec.skill_id.id,
                                    'job_description': rec.skill_id.job_description,
                                    'svc_desc': svc_desc,
                                    'svc_line': True,
                                    'out_of_office': after_hours,
                                    'holiday': holiday_rate,
                                    'rate_region_id': city_id.rate_country_id.rate_region_id.id,
                                    'country_id': city_id.rate_country_id.id,
                                    'language_ids': [(6, 0, language_ids)],
                                    'city_id': city_id.id,
                                    'svc_type_id': svc_type.id,
                                    'sla_id': sla.id,
                                    'worksite_id': worksite.id,
                                    'discount_fixed': rec.discount_fixed if rec.discount_fixed > 0 else 0,
                                    'discount': rec.discount if rec.discount > 0 else 0,
                                })

                    # for city_id in rec.city_ids:
                    #     language_ids = city_id.rate_country_id.language_ids.ids
                    #     service_type_line_id = rec.service_type_id.service_type_line_ids.filtered(
                    #         lambda l: l.rate_country_id == city_id.rate_country_id)
                    #     if service_type_line_id:
                    #         name = f'{city_id.rate_country_id.rate_region_id.name}, {city_id.rate_country_id.name}, {city_id.name}'
                    #         sequence = len(rec.order_line.filtered(lambda l: l.name.split('-')[0] == name))
                    #         previous_worksite = rec.order_line.filtered(lambda x: x.worksite_id.name == name)
                    #         if len(previous_worksite) == 0:
                    #             # Create WorkSite:
                    #             worksite = self.env['project.worksite'].create({
                    #                 'name': name,
                    #                 'city_id': city_id.id,
                    #                 'country_id': city_id.rate_country_id.id,
                    #                 'region_id': city_id.rate_country_id.rate_region_id.id,
                    #                 'sale_order_id': rec.id,
                    #             })
                    #         else:
                    #             worksite = self.env['project.worksite'].create({
                    #                 'name': name,
                    #                 'city_id': city_id.id,
                    #                 'country_id': city_id.rate_country_id.id,
                    #                 'region_id': city_id.rate_country_id.rate_region_id.id,
                    #                 'sale_order_id': rec.id,
                    #             })
                    #             worksite.sequence = previous_worksite[0].worksite_id.sequence + '-' + str(sequence)
                    #         # sequence = len(rec.order_line.filtered(lambda l: l.name.split('-')[0] == name))
                    #         name = name + '-' + str(sequence + 1)
                    #         svc_desc = f'{svc_type.name} - {rec.skill_id.name if rec.skill_id else ""}'
                    #         line_rate = service_type_line_id.rate
                    #
                    #         if rec.skill_id:
                    #             line_rate = self._get_uplift_rate(svc_type, rec.skill_id, service_type_line_id.rate)
                    #         if rec.out_of_office:
                    #             after_hours = after_hours_uplift
                    #         if rec.weekend:
                    #             holiday_rate = holiday_uplift
                    #             # Perform the creation of the order line
                    #         rec.order_line.create({
                    #             'order_id': rec.id,
                    #             'name': name,
                    #             'product_id': self.env.ref('rate_card.service_fee_product').id,
                    #             'product_uom_qty': self.env.ref('rate_card.service_fee_product').uom_id.id,
                    #             'price_unit': line_rate,
                    #             'skill_id': rec.skill_id.id,
                    #             'job_description': rec.skill_id.job_description,
                    #             'svc_desc': svc_desc,
                    #             'svc_line': True,
                    #             'out_of_office': after_hours,
                    #             'holiday': holiday_rate,
                    #             'rate_region_id': city_id.rate_country_id.rate_region_id.id,
                    #             'country_id': city_id.rate_country_id.id,
                    #             'language_ids': [(6, 0, language_ids)],
                    #             'city_id': city_id.id,
                    #             'svc_type_id': svc_type.id,
                    #             'sla_id': False,
                    #             'worksite_id': worksite.id,
                    #             'discount_fixed': rec.discount_fixed if rec.discount_fixed > 0 else 0,
                    #             'discount': rec.discount if rec.discount > 0 else 0,
                    #         })

            # Case when there is no SLA
            elif not rec.with_sla and rec.service_type_id:
                if not rec.city_ids:
                    for country_id in rec.country_ids:
                        language_ids = country_id.language_ids.ids
                        service_type_line_id = rec.service_type_id.service_type_line_ids.filtered(
                            lambda l: l.rate_country_id == country_id)
                        name = f'{country_id.rate_region_id.name}, {country_id.name}'
                        sequence = len(rec.order_line.filtered(lambda l: l.name.split('-')[0] == name))
                        previous_worksite = rec.order_line.filtered(lambda x: x.worksite_id.name == name)
                        if len(previous_worksite) == 0:
                            # Create WorkSite:
                            worksite = self.env['project.worksite'].create({
                                'name': name,
                                'country_id': country_id.id,
                                'region_id': country_id.rate_region_id.id,
                                'sale_order_id': rec.id,
                            })
                        else:
                            worksite = self.env['project.worksite'].create({
                                'name': name,
                                'country_id': country_id.id,
                                'region_id': country_id.rate_region_id.id,
                                'sale_order_id': rec.id,
                            })
                            worksite.sequence = previous_worksite[0].worksite_id.sequence + '-' + str(sequence)
                        name = name + '-' + str(sequence + 1)
                        svc_desc = f'{svc_type.name} - {rec.skill_id.name if rec.skill_id else ""}'
                        line_rate = service_type_line_id.rate
                        # Adjust rate based on skill and uplift type
                        if rec.skill_id:
                            line_rate = self._get_uplift_rate(rec.service_type_id, rec.skill_id, line_rate)
                        if rec.out_of_office:
                            after_hours = after_hours_uplift
                        if rec.weekend:
                            holiday_rate = holiday_uplift
                            # Perform the creation of the order line
                        rec.order_line.create({
                            'order_id': rec.id,
                            'name': name,
                            'product_id': self.env.ref('rate_card.service_fee_product').id,
                            'product_uom_qty': self.env.ref('rate_card.service_fee_product').uom_id.id,
                            'price_unit': line_rate,
                            'skill_id': rec.skill_id.id,
                            'job_description': rec.skill_id.job_description,
                            'svc_desc': svc_desc,
                            'svc_line': True,
                            'out_of_office': after_hours,
                            'holiday': holiday_rate,
                            'rate_region_id': country_id.rate_region_id.id,
                            'country_id': country_id.id,
                            'language_ids': [(6, 0, language_ids)],
                            'svc_type_id': svc_type.id,
                            'sla_id': False,
                            'worksite_id': worksite.id,
                            'discount_fixed': rec.discount_fixed if rec.discount_fixed > 0 else 0,
                            'discount': rec.discount if rec.discount > 0 else 0,
                        })

                else:
                    for city_id in rec.city_ids:
                        language_ids = city_id.rate_country_id.language_ids.ids
                        name = f'{city_id.rate_country_id.rate_region_id.name}, {city_id.rate_country_id.name}, {city_id.name}'
                        sequence = len(rec.order_line.filtered(lambda l: l.name.split('-')[0] == name))
                        previous_worksite = rec.order_line.filtered(lambda x: x.worksite_id.name == name)
                        if len(previous_worksite) == 0:
                            # Create WorkSite:
                            worksite = self.env['project.worksite'].create({
                                'name': name,
                                'city_id': city_id.id,
                                'country_id': city_id.rate_country_id.id,
                                'region_id': city_id.rate_country_id.rate_region_id.id,
                                'sale_order_id': rec.id,
                            })
                        else:
                            worksite = self.env['project.worksite'].create({
                                'name': name,
                                'city_id': city_id.id,
                                'country_id': city_id.rate_country_id.id,
                                'region_id': city_id.rate_country_id.rate_region_id.id,
                                'sale_order_id': rec.id,
                            })
                            worksite.sequence = previous_worksite[0].worksite_id.sequence + '-' + str(sequence)
                        name = name + '-' + str(sequence + 1)
                        svc_desc = f'{svc_type.name} - {rec.skill_id.name if rec.skill_id else ""}'
                        service_type_line_id = rec.service_type_id.service_type_line_ids.filtered(
                            lambda l: l.rate_country_id == city_id.rate_country_id)
                        line_rate = service_type_line_id.rate
                        if rec.skill_id:
                            line_rate = self._get_uplift_rate(rec.service_type_id, rec.skill_id, line_rate)
                        if rec.out_of_office:
                            after_hours = after_hours_uplift
                        if rec.weekend:
                            holiday_rate = holiday_uplift
                            # Perform the creation of the order line
                        rec.order_line.create({
                            'order_id': rec.id,
                            'name': name,
                            'product_id': self.env.ref('rate_card.service_fee_product').id,
                            'product_uom_qty': self.env.ref('rate_card.service_fee_product').uom_id.id,
                            'price_unit': line_rate,
                            'skill_id': rec.skill_id.id,
                            'job_description': rec.skill_id.job_description,
                            'svc_desc': svc_desc,
                            'svc_line': True,
                            'out_of_office': after_hours,
                            'holiday': holiday_rate,
                            'rate_region_id': city_id.rate_country_id.rate_region_id.id,
                            'country_id': city_id.rate_country_id.id,
                            'language_ids': [(6, 0, language_ids)],
                            'city_id': city_id.id,
                            'svc_type_id': svc_type.id,
                            'sla_id': False,
                            'worksite_id': worksite.id,
                            'discount_fixed': rec.discount_fixed if rec.discount_fixed > 0 else 0,
                            'discount': rec.discount if rec.discount > 0 else 0,
                        })
            rec.discount_fixed = 0.0
            rec.discount = 0.0

    def _get_uplift_rate(self, svc_sla_id, skill_id, rate):
        """
        :param svc_sla_id: The project.sla or service.type record that contains the uplift rates
        :param skill_id: The project.skill record
        :param rate: The original rate that needs to be uplifted
        :return: The uplifted rate
        """
        multiplier = 1
        if skill_id.id in svc_sla_id.rate_uplift_line_ids.mapped('project_skill_id').ids:
            while skill_id:
                multiplier *= svc_sla_id.rate_uplift_line_ids.filtered(
                    lambda l: l.project_skill_id == skill_id).multiplier_rate or 1
                skill_id = skill_id.project_skill_parent_id
        return rate * multiplier

    # === ACTION METHODS ===#
    # Discount Wizard
    def action_open_discount_wizard(self):
        self.ensure_one()
        return {
            'name': _("Discount"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.discount',
            'view_mode': 'form',
            'view_id': self.env.ref('rate_card.sale_order_line_wizard_form').id,
            'target': 'new',
        }

    # WorkSite Smart Button Action
    def action_view_worksite(self):
        self.ensure_one()
        action = self.env.ref('rate_card.project_worksite_action').read()[0]
        action.update({
            'domain': [('sale_order_line_id', 'in', self.order_line.ids)],
        })
        return action

    def action_open_import_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Countries',
            'res_model': 'rate.card.country.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('rate_card.view_import_country_wizard_form').id,
            'target': 'new',
            'context': {'default_sale_order_id': self.id},
        }
