# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class RateRegion(models.Model):
    _name = 'rate.region'
    _description = "Rate Region"
    _rec_name= "name"
    _inherit = [
                'mail.thread',
                'mail.activity.mixin',
               ]

    sequence = fields.Char(string='Sequence',help='Used to order Rate Region in the tree view', tracking=True)
    name = fields.Char(string='Region Name', required=True, translate=True, tracking=True)
    rate_country_line_ids = fields.One2many('rate.country', 'rate_region_id', string='Regions', tracking=True)
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)

    # CRUD Functions
    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record for a model RateRegion
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for value in vals_list:
            value['sequence'] = self.env['ir.sequence'].next_by_code('rate_region') or _('New')
        result = super(RateRegion, self).create(vals_list)
    
        return result
