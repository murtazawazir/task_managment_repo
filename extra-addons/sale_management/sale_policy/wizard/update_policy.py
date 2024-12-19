from odoo import fields,models

class UpdatePolicy(models.Model):
    _name = 'update.policy'

    price_list = fields.Many2one('product.pricelist', string='Price List')
    sale_policy_id = fields.Many2one('sale.policy',string='Sale Policy')