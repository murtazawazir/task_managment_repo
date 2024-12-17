# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class RateCity(models.Model):
    _name = 'rate.city'
    _description = "Rate City"
    _rec_name = "name"
    _inherit = [
                'mail.thread',
                'mail.activity.mixin',
               ]

    sequence = fields.Char(string='Sequence',help='Used to order Project City in the tree view', tracking=True)
    serial_number = fields.Integer(string='Serial', compute='_compute_serial_number', store=True)
    name = fields.Char(string='City Name', required=True, translate=True, tracking=True)
    rate_country_id = fields.Many2one(
        string='Country',
        comodel_name='rate.country',
        ondelete='cascade',
        tracking=True,
    )

    rate_city_line_ids = fields.One2many('rate.city.line', 'rate_city_id', string='Rate City Lines')


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
        currency_field='currency_id',  tracking=True, compute="_compute_country_rate",
    )
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)

        # Rate
    @api.depends('rate_country_id','rate_country_id.rate')
    def _compute_country_rate(self):
        for record in self:
            if record.rate_country_id:
                record.rate = record.rate_country_id.rate
            else:
                record.rate = 0

        # Serial Number
    @api.depends('rate_country_id.city_ids')
    def _compute_serial_number(self):
        for record in self:
            if record.rate_country_id:
                for idx, child in enumerate(record.rate_country_id.city_ids, start=1):
                    child.serial_number = idx

    @api.depends('company_id')
    def _compute_company_id(self):
        for record in self:
            if not record.company_id:
                companies = self.env['res.company'].search([])
                if len(companies) == 1:
                    record.company_id = companies[0]


    # CRUD Function
    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record for a model RateCity
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for value in vals_list:
            value['sequence'] = self.env['ir.sequence'].next_by_code('rate_city') or _('New')
        result = super(RateCity, self).create(vals_list)
    
        return result


class ProjectSLALine(models.Model):
    _name = 'rate.city.line'
    _description = "Rate City Lines"
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    
    rate_city_id = fields.Many2one(
        string='Rate City',
        comodel_name='rate.city',
        ondelete='cascade',
    )

    name = fields.Char(string='Name', required=True, translate=True, tracking=True)


    