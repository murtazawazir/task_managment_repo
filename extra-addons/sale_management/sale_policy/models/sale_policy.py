from odoo import fields, models, api
from odoo.addons.test_convert.tests.test_env import record
from odoo.exceptions import ValidationError


class SalePolicy(models.Model):
    _name = 'sale.policy'
    _description = 'This module is about sale policy'

    # Character Fields

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    policy_type = fields.Char(string='Policy Type')


    # Many2one Fields
    company_id = fields.Many2one('res.company', string='Company')

    # Boolean Fields

    is_credit = fields.Boolean(string='Is Credit')
    is_secure_credit = fields.Boolean(string='Is Secure Credit')
    is_bg_allowed = fields.Boolean(string='Is BG Allowed')
    temporary_credit_limit = fields.Boolean(string='Temporary Credit Limit')
    is_active = fields.Boolean(string='Is Active')
    is_sale_active = fields.Boolean(string='Is Sale Active')
    is_collection_active = fields.Boolean(string='Is Collection Active')

    # Date Fields
    collections_start_date = fields.Date(string='Collections Start Date')
    collections_end_date = fields.Date(string='Collections End Date')
    sale_start_date = fields.Date(string='Sale Start Date')
    sale_end_date = fields.Date(string='Sale End Date')

    # Integer Fields

    collections_grace_period = fields.Integer(string='Collections Grace Period')
    sale_grace_period = fields.Integer(string='Sale Grace Period')

    # Statusbar Field
    status = fields.Selection(
        [('draft', 'Draft'), ('approved1', 'Approved1'), ('approved2', 'Approved2'), ('approved', 'Approved')])

    # One2many Fields
    sale_policy_line_ids = fields.One2many('sale.policy.line', 'sale_policy_id', string='Sale Policy Line')

    def export_button(self):
        pass

    def import_product(self):
        create_wizard = {
            'name' : 'Wizard',
            'type' : 'ir.actions.act_window',
            'res_model' : 'wizard.wizard',
            'target': 'new',
           'view_mode': 'form',
           'view_type': 'form',
        }
        return create_wizard





class SalePolicyLine(models.Model):
    _name = 'sale.policy.line'

    # Many2one Fields

    sale_policy_id = fields.Many2one('sale.policy')
    product_id = fields.Many2one('product.product', string='Product')
    product_category_id = fields.Many2one('product.category', string='Product Category')
    product_template_id = fields.Many2one('product.template', string='Product Template')

    # Float Fields

    unit_of_measure = fields.Float(string='Unit Of Measure')
    price_list_discount = fields.Float(string='Price List Discount')
    extra_discount = fields.Float(string='Extra Discount')
    discount_amount = fields.Float(string='Discount Amount')
    net_amount = fields.Float(string='Net Amount')
