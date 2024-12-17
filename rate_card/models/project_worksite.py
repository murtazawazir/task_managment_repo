# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProjectWorksite(models.Model):
    _name = 'project.worksite'
    _description = "Project Worksite"
    _rec_name = 'name'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    sequence = fields.Char(string='Sequence', help='Used to order Project Worksite in the tree view', tracking=True)
    serial_number = fields.Integer(string='Serial', store=True)  # compute='_compute_serial_number'
    name = fields.Char(string='Name', required=True, translate=True, tracking=True)
    project_rate_id = fields.Many2one(
        string='Project Rate',
        comodel_name='project.project.rate',
        ondelete='cascade',
    )
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)
    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        ondelete='cascade',
    )

    sale_order_line_id = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='worksite_id',
        string='Sale Order',
        tracking=True
    )

    # address fields
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city_id = fields.Many2one("rate.city",string='City',  ondelete='restrict', domain="[('rate_country_id', '=?', country_id)]")
    country_id = fields.Many2one('rate.country', string='Country', ondelete='restrict', domain="[('rate_region_id', '=?', region_id)]" )
    region_id = fields.Many2one('rate.region', string='Region', ondelete='restrict')

    def _compute_display_name(self):
        res = super(ProjectWorksite, self)._compute_display_name()
        for project_worksite in self:
            if project_worksite.sequence and project_worksite.name:
                project_worksite.display_name = "%s - %s" % (project_worksite.name,project_worksite.sequence)
            elif project_worksite.sequence:
                project_worksite.display_name = project_worksite.sequence
            elif project_worksite.name:
                project_worksite.display_name = project_worksite.name

    # CRUD Functions
    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record for a model ProjectWorksite
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for value in vals_list:
            value['sequence'] = self.env['ir.sequence'].next_by_code('project_worksite') or _('New')
        result = super(ProjectWorksite, self).create(vals_list)

        return result
