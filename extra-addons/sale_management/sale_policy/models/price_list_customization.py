from odoo import models,fields,api
from odoo.tools.populate import compute


class ProductList(models.Model):
    _inherit = 'product.pricelist.item'


    discount = fields.Float(string='Discount')
    discount_amount = fields.Float(string='Discount Amount')
    net_amount = fields.Float(string='Net Amout',compute='_compute_methods')

    @api.depends('discount','discount_amount')
    def _compute_methods(self):
        for rec in self:
            self.net_amount = rec.fixed_price + rec.discount_amount / rec.discount

