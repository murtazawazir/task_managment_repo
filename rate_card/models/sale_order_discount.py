# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderDiscount(models.TransientModel):
    _inherit = 'sale.order.discount'

    @api.onchange('discount_amount','discount_percentage')
    def _set_discount_type(self):
        for wizard in self:
            if wizard.discount_amount > 0:
                wizard.discount_type = 'amount'
            elif wizard.discount_percentage > 1:
                wizard.discount_type = 'so_discount'
            else:
                wizard.discount_type = 'sol_discount'
    

    def _create_discount_lines(self):
        """Create SOline(s) according to wizard configuration"""
        self.ensure_one()
        discount_product = self._get_discount_product()

        if self.discount_type == 'amount':
            if self.discount_amount <= self.sale_order_id.amount_total:
                vals_list = [
                    self._prepare_discount_line_values(
                        product=discount_product,
                        amount=self.discount_amount,
                        taxes=self.env['account.tax'],
                    )
                ]
            else:
                raise ValidationError(_("Invalid discount amount, Discount Amount [%s] should be less than SO total amount [%s]" % (self.discount_amount,self.sale_order_id.amount_total)))
        else: # so_discount
            total_price_per_tax_groups = defaultdict(float)
            for line in self.sale_order_id.order_line:
                if not line.product_uom_qty or not line.price_unit:
                    continue

                total_price_per_tax_groups[line.tax_id] += line.price_subtotal

            if not total_price_per_tax_groups:
                # No valid lines on which the discount can be applied
                return
            elif len(total_price_per_tax_groups) == 1:
                # No taxes, or all lines have the exact same taxes
                taxes = next(iter(total_price_per_tax_groups.keys()))
                subtotal = total_price_per_tax_groups[taxes]
                vals_list = [{
                    **self._prepare_discount_line_values(
                        product=discount_product,
                        amount=subtotal * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Discount: %(percent)s%%",
                            percent=self.discount_percentage*100
                        ),
                    ),
                }]
            else:
                vals_list = [
                    self._prepare_discount_line_values(
                        product=discount_product,
                        amount=subtotal * self.discount_percentage,
                        taxes=taxes,
                        description=_(
                            "Discount: %(percent)s%%"
                            "- On products with the following taxes %(taxes)s",
                            percent=self.discount_percentage*100,
                            taxes=", ".join(taxes.mapped('name'))
                        ),
                    ) for taxes, subtotal in total_price_per_tax_groups.items()
                ]
        return self.env['sale.order.line'].create(vals_list)


