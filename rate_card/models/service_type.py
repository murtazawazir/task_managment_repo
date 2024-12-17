# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ServiceType(models.Model):
    _name = 'service.type'
    _description = "Service Type"
    _rec_name = 'name'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    sequence = fields.Char(string='Sequence', help='Used to order Service Type in the tree view', tracking=True)
    name = fields.Char(string='Name', required=True, translate=True, tracking=True)
    with_sla = fields.Boolean(string='SLA Enabled', tracking=True, required=False)
    rate_basis = fields.Selection(string='Rate Basis',
                                  selection=[('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly'),
                                             ('monthly', 'Monthly')],
                                  default="hourly")
    # In Project SLA we have rate_basis field and here we have rate_bases, so have changed field name to rate_basis
    # rate_bases = fields.Selection(string='Rate Basis',
    #                               selection=[('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly'),
    #                                          ('monthly', 'Monthly')],
    #                               default="hourly")
    service_type_line_ids = fields.One2many('service.type.line', 'service_type_id', string='Service Type Lines')
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)
    rate_uplift_line_ids = fields.One2many(comodel_name='rate.uplift.line', inverse_name='service_type_id',
                                           string='Rate Uplift Line', required=False, tracking=True)

    # CRUD
    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record for a model Service Type
            @param values: provides a data for new record

            @return: returns a id of new record
        """
        for value in vals_list:
            value['sequence'] = self.env['ir.sequence'].next_by_code('service_type') or _('New')
        result = super(ServiceType, self).create(vals_list)

        return result


class ServiceTypeLine(models.Model):
    _name = 'service.type.line'
    _description = "Service Type Lines"
    
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    service_type_id = fields.Many2one(
        string='Service Type',
        comodel_name='service.type',
        ondelete='cascade',
    )

    rate_country_id = fields.Many2one(
        comodel_name='rate.country',
        string='Country',
        required=False, tracking=True)

    rate = fields.Monetary(
        string='Rate',
        required=False, tracking=True, currency_field='currency_id')

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        compute="_compute_currency_id")    
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)

    @api.depends('currency_id')
    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = self.env.ref('base.USD').id
