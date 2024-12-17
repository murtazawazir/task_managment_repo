# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProjectSLA(models.Model):
    _name = 'project.sla'
    _description = "Project SLA"
    _rec_name = 'name'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    sequence = fields.Char(string='Sequence', help='Used to order Project SLA in the tree view', tracking=True)
    name = fields.Char(string='SLA Name', required=True, translate=True, tracking=True)
    project_sla_line_ids = fields.One2many('project.sla.line', 'project_sla_id', string='Project SLA Lines')
    rate_basis = fields.Selection(
        [('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], default='hourly')
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)
    rate_uplift_line_ids= fields.One2many(comodel_name='rate.uplift.line', inverse_name='project_sla_id',string='Rate Uplift Line',required=False,tracking=True)

    # CRUD
    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record for a model ProjectSLA
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for value in vals_list:
            value['sequence'] = self.env['ir.sequence'].next_by_code('project_sla') or _('New')
        result = super(ProjectSLA, self).create(vals_list)
        return result
