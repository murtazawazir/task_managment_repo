from itertools import product

from odoo import fields, models
from odoo.addons.test_convert.tests.test_env import record


class Wizard(models.TransientModel):
    _name = 'wizard.wizard'

    import_type = fields.Selection(
        [('product', 'Product'), ('category', 'Category'), ('template', 'Template'), ('sale_policy', 'Sale Policy'), ])
    product_ids = fields.Many2many('product.product', string='Product')
    product_category = fields.Many2one('product.category', string='Product Category')
    product_template = fields.Many2one('product.template', string='Product Template')
    sale_policy_id = fields.Many2one('sale.policy', string='Sale Policy')

    # price_list = fields.Many2one('price.list', string='Price List')

    def import_product(self):
        if self.product_category:
            if self.env.context.get('active_id'):
                products = self.env['product.product'].search([('categ_id', '=', self.product_category.id)])
                policy = self.sale_policy_id.browse(self.env.context.get('active_id'))
                policy.sale_policy_line_ids = None
                policy.sale_policy_line_ids = [(0, 0, {
                    'product_id': rec.id,
                }) for rec in products]
        elif self.product_ids:
            products = self.env['product.product'].search([('id', '=', self.product_ids.ids)])
            policy = self.sale_policy_id.browse(self.env.context.get('active_id'))
            policy.sale_policy_line_ids = None
            policy.sale_policy_line_ids = [(0, 0, {
                'product_id': rec.id,
            }) for rec in products]

        elif self.sale_policy_id:
            policy = self.sale_policy_id.browse(self.env.context.get('active_id'))
            policy.sale_policy_line_ids = None
            policy.sale_policy_line_ids = [(0, 0, {
                'product_id': rec.product_id.id
            }) for rec in self.sale_policy_id.sale_policy_line_ids]

