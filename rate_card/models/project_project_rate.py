# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectProjectRate(models.Model):
    _name = 'project.project.rate'
    _description = "Project Rate"
    _rec_name = 'display_name'
    _inherit = [
                'mail.thread',
                'mail.activity.mixin',
               ]

    sequence = fields.Char(string='Sequence',help='Used to order Project Rate in the tree view', tracking=True)
    name = fields.Char(string='Name', required=True, translate=True, tracking=True)
    rate_country_id = fields.Many2one(
        string='Country',
        comodel_name='rate.country',
        ondelete='cascade',
        tracking=True,
    )
    project_worksite_ids = fields.One2many('project.worksite', 'project_rate_id', string='Project Worksites')
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)

    # Depend Function
        #Display Name
    def _compute_display_name(self):
        res = super(ProjectProjectRate, self)._compute_display_name()
        for project_project_rate in self:
            if project_project_rate.sequence and project_project_rate.name:
                project_project_rate.display_name = "%s - %s" % (project_project_rate.sequence,project_project_rate.name)
            elif project_project_rate.sequence:
                project_project_rate.display_name = project_project_rate.sequence
            elif project_project_rate.name:
                project_project_rate.display_name = project_project_rate.name

    # CRUD Fucntion
    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record for a model ProjectProjectRate
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for value in vals_list:
            value['sequence'] = self.env['ir.sequence'].next_by_code('project_project_rate') or _('New')
        result = super(ProjectProjectRate, self).create(vals_list)
    
        return result
