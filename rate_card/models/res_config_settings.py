from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fixed_line_discount = fields.Boolean(string='Fixed discount (line-wise)', implied_group='rate_card.group_fixed_discount_per_so_line')
    percentage_line_discount = fields.Boolean(string='Percentage discount (line-wise)', implied_group='product.group_fixed_discount_per_so_line')
    fixed_total_discount = fields.Boolean(string='Fixed discount (Total)')
    percentage_total_discount = fields.Boolean(string='Percentage discount (Total)')
    holiday_uplift = fields.Float(string='Holiday Raise')
    after_hours_uplift = fields.Float(string='OOH Raise')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('sale.holiday_uplift', self.holiday_uplift)
        self.env['ir.config_parameter'].set_param('sale.after_hours_uplift', self.after_hours_uplift)
        if self.fixed_line_discount != bool(self.env['ir.config_parameter'].sudo().get_param('sale.fixed_line_discount')):
            if self.fixed_line_discount:
                group = self.env.ref('rate_card.group_fixed_discount_per_so_line')
                if group:
                    if group not in self.env.user.groups_id:
                        self.env.user.groups_id = [(4, group.id)]
            else:
                group = self.env.ref('rate_card.group_fixed_discount_per_so_line')
                if group:
                    if group in self.env.user.groups_id:
                        self.env.user.groups_id = [(3, group.id)]
                
        if self.percentage_line_discount != bool(self.env['ir.config_parameter'].sudo().get_param('sale.percentage_line_discount')):
            if self.percentage_line_discount:
                group = self.env.ref('rate_card.group_percentage_discount_per_so_line')
                if group:
                    if group not in self.env.user.groups_id:
                        self.env.user.groups_id = [(4, group.id)]
            else:
                group = self.env.ref('rate_card.group_percentage_discount_per_so_line')
                if group:
                    if group in self.env.user.groups_id:
                        self.env.user.groups_id = [(3, group.id)]

        # if self.fixed_total_discount != bool(self.env['ir.config_parameter'].sudo().get_param('sale.fixed_total_discount')):
        #     if self.fixed_total_discount:
        #         group = self.env.ref('rate_card.group_fixed_discount_total')
        #         if group:
        #             if group not in self.env.user.groups_id:
        #                 self.env.user.groups_id = [(4, group.id)]
        #     else:
        #         group = self.env.ref('rate_card.group_fixed_discount_total')
        #         if group:
        #             if group in self.env.user.groups_id:
        #                 self.env.user.groups_id = [(3, group.id)]

        # if self.percentage_total_discount != bool(self.env['ir.config_parameter'].sudo().get_param('sale.percentage_total_discount')):
        #     if self.percentage_total_discount:
        #         group = self.env.ref('rate_card.group_percentage_discount_total')
        #         if group:
        #             if group not in self.env.user.groups_id:
        #                 self.env.user.groups_id = [(4, group.id)]
        #     else:
        #         group = self.env.ref('rate_card.group_percentage_discount_total')
        #         if group:
        #             if group in self.env.user.groups_id:
        #                 self.env.user.groups_id = [(3, group.id)]

        self.env['ir.config_parameter'].set_param('sale.fixed_line_discount', self.fixed_line_discount)
        self.env['ir.config_parameter'].set_param('sale.percentage_line_discount', self.percentage_line_discount)
        self.env['ir.config_parameter'].set_param('sale.fixed_total_discount', self.fixed_total_discount)
        self.env['ir.config_parameter'].set_param('sale.percentage_total_discount', self.percentage_total_discount)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            group_discount_per_so_line = self.env['ir.config_parameter'].get_param('product.group_discount_per_so_line', default=False),
            fixed_line_discount=self.env['ir.config_parameter'].get_param('sale.fixed_line_discount', default=False),
            percentage_line_discount=self.env['ir.config_parameter'].get_param('sale.percentage_line_discount', default=False),
            fixed_total_discount=self.env['ir.config_parameter'].get_param('sale.fixed_total_discount', default=False),
            percentage_total_discount=self.env['ir.config_parameter'].get_param('sale.percentage_total_discount', default=False),
            holiday_uplift=self.env['ir.config_parameter'].get_param('sale.holiday_uplift', default=1),
            after_hours_uplift=self.env['ir.config_parameter'].get_param('sale.after_hours_uplift', default=1),
        )
        return res