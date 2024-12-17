# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RateUpliftLine(models.Model):
    _name = 'rate.uplift.line'
    _description = "Rate Uplift Lines"
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]

    project_sla_id = fields.Many2one(
        string='Project SLA',
        comodel_name='project.sla',
        ondelete='cascade',
    )

    project_skill_id = fields.Many2one(
        comodel_name='project.skill',
        string='Skillset',
        tracking=True)

    service_type_id = fields.Many2one(
        string='Service Type',
        comodel_name='service.type',
        ondelete='cascade',
    )

    multiplier_rate = fields.Float(
        string='Multiplier',
        required=False, tracking=True, digits=(30, 4))

    @api.constrains('country_id', 'project_sla_id')
    def _check_unique_skillset(self):
        for record in self:
            same_skillset_lines = self.env['rate.uplift.line'].search([
                ('project_skill_id', '=', record.project_skill_id.id),
                ('project_sla_id', '=', record.project_sla_id.id),
                ('id', '!=', record.id)
            ])
            if same_skillset_lines:
                raise ValidationError("The same skillset cannot ce selected more than once!")
