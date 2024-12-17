# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class RateCountry(models.Model):
    _name = 'rate.country'
    _description = "Country"
    _rec_name = "name"
    _inherit = [
                'mail.thread',
                'mail.activity.mixin',
               ]

    sequence = fields.Char(string='Sequence',help='Used to order Project Country in the tree view', tracking=True)
    serial_number = fields.Integer(string='Serial', compute='_compute_serial_number', store=True)
    name = fields.Char(string='Country Name', required=True, translate=True, tracking=True)
    city_ids = fields.One2many('rate.city', 'rate_country_id', string='Cities', tracking=True)
    rate_region_id = fields.Many2one(
        string='Region',
        comodel_name='rate.region',
        ondelete='cascade',
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company', compute='_compute_company_id',
        store=True, readonly=False, index=True,
    )

    currency_id = fields.Many2one(
        string='Company Currency',
        related='company_id.currency_id', readonly=True,
    )

    rate = fields.Monetary(
        string='Rate', store=True, 
        currency_field='currency_id',  tracking=True
    )
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)
    language_ids = fields.Many2many(
        comodel_name='res.lang',
        relation='res_country_res_lang_rel',
        column1='country_id',
        column2='lang_id',
        string='Languages'
    )

        # Serial Number
    @api.depends('rate_region_id.rate_country_line_ids')
    def _compute_serial_number(self):
        for record in self:
            if record.rate_region_id:
                for idx, child in enumerate(record.rate_region_id.rate_country_line_ids, start=1):
                    child.serial_number = idx

    @api.depends('company_id')
    def _compute_company_id(self):
        for record in self:
            if not record.company_id:
                companies = self.env['res.company'].search([])
                if len(companies) == 1:
                    record.company_id = companies[0]

    # CRUD
    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record for a model RateCountry
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for value in vals_list:
            value['sequence'] = self.env['ir.sequence'].next_by_code('rate_country') or _('New')
        result = super(RateCountry, self).create(vals_list)
    
        return result
 
