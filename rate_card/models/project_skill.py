# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectSkill(models.Model):
    _name = 'project.skill'
    _description = "Project Skill"
    _rec_name = 'name'
    _inherit = [
                'mail.thread',
                'mail.activity.mixin',
               ]

    sequence = fields.Char(string='Sequence',help='Used to order Project Skill in the tree view', tracking=True)
    name = fields.Char(string='Skill Name', required=True, translate=True, tracking=True)
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)
    project_skill_parent_id = fields.Many2one(
        comodel_name='project.skill',
        string='Parent Skill',
        required=False)
    job_description = fields.Html(string='Description', sanitize_attributes=False)

    # CRUD Function

    @api.model_create_multi
    def create(self, vals_list):
        """
            Create a new record for a model ProjectSkill
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for value in vals_list:
            value['sequence'] = self.env['ir.sequence'].next_by_code('project_skill') or _('New')
        result = super(ProjectSkill, self).create(vals_list)
    
        return result