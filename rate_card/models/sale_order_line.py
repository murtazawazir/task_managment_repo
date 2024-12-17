from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_round


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]
    _description = 'Sale Orde Line'

    skill_id = fields.Many2one(
        string='Skill',
        comodel_name='project.skill',
        ondelete='cascade',
    )

    svc_desc = fields.Char(string='Service Description')

    svc_line = fields.Boolean(default=False)

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits="Product Price",
        help="Fixed amount discount.",
    )

    rate_region_id = fields.Many2one(
        comodel_name='rate.region',
        string='Region',
        required=False)
    country_id = fields.Many2one(
        comodel_name='rate.country',
        string='Country',
        required=False)

    city_id = fields.Many2one(
        comodel_name='rate.city',
        string='City',
        required=False)

    svc_type_id = fields.Many2one(
        comodel_name='service.type',
        string='Service Type',
        required=False)

    sla_id = fields.Many2one(
        comodel_name='project.sla',
        string='SLA',
        required=False)

    worksite_travel_cost = fields.Monetary(
        string='Expenses',
        currency_field='currency_id',
        required=False
    )
    worksite_id = fields.Many2one(
        string='WorkSite',
        comodel_name='project.worksite',
        ondelete='cascade',
    )
    street = fields.Char(related='worksite_id.street',
                         store=True)
    street2 = fields.Char(related='worksite_id.street2', store=True)
    zip = fields.Char(change_default=True, related='worksite_id.zip', store=True)
    address_line = fields.Char(string='Address Line', compute='_address_line', store=True)

    with_sla = fields.Boolean(string='SLA Enabled', tracking=True, required=False,
                              related="svc_type_id.with_sla")  # related="order_id.with_sla"
    out_of_office = fields.Float(string='OOH hide')
    holiday = fields.Float(string='Weekend/PH hide')

    out_of_office_display = fields.Char(
        string='OOH',
        compute='_compute_out_of_office_display',
        inverse='_inverse_out_of_office_display',
        store=True
    )

    holiday_display = fields.Char(
        string='Weekend/PH',
        compute='_compute_holiday_display',
        inverse='_inverse_holiday_display',
        store=True
    )
    language_ids = fields.Many2many(
        comodel_name='res.lang',
        relation='sale_order_line_res_lang_rel',
        column1='order_line_id',
        column2='lang_id',
        string='Languages'
    )
    job_description = fields.Html(string='JD', sanitize_attributes=False)

    invoice_id = fields.Many2one(string='Invoice', ondelete='cascade', comodel_name='account.move')

    @api.depends('street', 'street2')
    def _address_line(self):
        for record in self:
            if record.street and record.street2:
                record.address_line = record.street + ', ' + record.street2
            elif record.street:
                record.address_line = record.street
            elif record.street2:
                record.address_line = record.street2

    @api.depends('out_of_office')
    def _compute_out_of_office_display(self):
        for record in self:
            record.out_of_office_display = f'{record.out_of_office:.2f} X' if record.out_of_office else ''

    def _inverse_out_of_office_display(self):
        for record in self:
            if record.out_of_office_display:
                value = record.out_of_office_display.replace("X", "").strip()
                try:
                    record.out_of_office = float(value)
                except ValueError:
                    record.out_of_office = 0.0

    @api.depends('holiday')
    def _compute_holiday_display(self):
        for record in self:
            record.holiday_display = f'{record.holiday:.2f} X' if record.holiday else ''

    def _inverse_holiday_display(self):
        for record in self:
            if record.holiday_display:
                value = record.holiday_display.replace("X", "").strip()
                try:
                    record.holiday = float(value)
                except ValueError:
                    record.holiday = 0.0

    @api.depends('product_id', 'product_uom', 'product_uom_qty', )
    def _compute_price_unit(self):
        for line in self:
            if line.svc_line:
                continue
            super(SaleOrderLine, line)._compute_price_unit()

    @api.depends('order_id')
    def _compute_show_percentage_discount(self):
        percentage_line_discount = self.env['ir.config_parameter'].sudo().get_param('sale.percentage_line_discount')
        for line in self:
            line.show_percentage_discount = bool(percentage_line_discount)

    @api.constrains("discount_fixed", "discount")
    def _check_discounts(self):
        """Check that the fixed discount and the discount percentage are consistent."""
        for line in self:
            if line.discount:
                if line.discount > 100:
                    raise ValidationError(
                        _("Invalid discount Percentage, Discount Percentage [%s] should be less than or equal to 100" % (
                            self.discount)))

            if line.discount_fixed and line.discount:
                # if line.discount_fixed > 
                currency = line.currency_id
                calculated_fixed_discount = float_round(
                    line._get_discount_from_fixed_discount(),
                    precision_rounding=currency.rounding,
                )

                if (float_compare(calculated_fixed_discount, line.discount,
                                  precision_rounding=currency.rounding, ) != 0):
                    raise ValidationError(
                        _("The fixed discount %(fixed)s does not match the calculated "
                          "discount %(discount)s %%. Please correct one of the discounts.")
                        % {"fixed": line.discount_fixed, "discount": line.discount, }
                    )

    def _convert_to_tax_base_line_dict(self):
        """Prior to calculating the tax totals for a line, update the discount value
        used in the tax calculation to the full float value. Otherwise, we get rounding
        errors in the resulting calculated totals.

        For example:
            - price_unit = 750.0
            - discount_fixed = 100.0
            - discount = 13.33
            => price_subtotal = 650.03

        :return: A python dictionary.
        """
        self.ensure_one()

        # Accurately pass along the fixed discount amount to the tax computation method.
        if self.discount_fixed:
            return self.env["account.tax"]._convert_to_tax_base_line_dict(
                self,
                partner=self.order_id.partner_id,
                currency=self.order_id.currency_id,
                product=self.product_id,
                taxes=self.tax_id,
                price_unit=self.price_unit,
                quantity=self.product_uom_qty,
                discount=self._get_discount_from_fixed_discount(),
                price_subtotal=self.price_subtotal,
            )

        return super()._convert_to_tax_base_line_dict()

    @api.onchange("discount_fixed", "price_unit")
    def _onchange_discount_fixed(self):
        if not self.discount_fixed:
            return
        elif self.discount_fixed > self.price_unit:
            raise ValidationError(_("Invalid discount amount, Discount Amount [%s] should be less than Price [%s]" % (
                self.discount_fixed, self.price_unit)))
        self.discount = self._get_discount_from_fixed_discount()

    def _get_discount_from_fixed_discount(self):
        """Calculate the discount percentage from the fixed discount amount."""
        self.ensure_one()
        if not self.discount_fixed:
            return 0.0

        return ((self.price_unit != 0) and ((self.discount_fixed) / self.price_unit) * 100 or 0.00)

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        res.update({"discount_fixed": self.discount_fixed})
        return res

    def action_create_invoice(self):
        self.ensure_one()

        invoice_vals = self.order_id._prepare_invoice()
        invoice = self.env['account.move'].create(invoice_vals)
        invoice_line_vals = self._prepare_account_move_line(invoice.id)
        self.env['account.move.line'].create(invoice_line_vals)
        self.invoice_id = invoice.id
        return True

    def _prepare_account_move_line(self, invoice_id):
        return {
            'move_id': invoice_id,
            'name': self.name,
            'quantity': self.product_uom_qty,
            'price_unit': self.price_unit,
            'product_id': self.product_id.id,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'sale_line_ids': [(6, 0, [self.id])],
            'account_id': self.product_id.property_account_income_id.id or self.product_id.categ_id.property_account_income_categ_id.id,
        }
