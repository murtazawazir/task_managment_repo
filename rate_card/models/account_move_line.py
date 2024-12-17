from odoo import models, api, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    discount_fixed = fields.Float(
            string="Discount (Fixed)",
            digits="Product Price",
            help="Fixed amount discount.",
        )