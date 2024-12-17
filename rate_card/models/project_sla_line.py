# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProjectSLA(models.Model):
    _name = 'project.sla.line'
    _description = "Project SLA Line"

    country_id = fields.Many2one(
        string='Country',
        comodel_name='rate.country',
        ondelete='cascade'
    )
    currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_currency_id'
    )

    rate = fields.Monetary(
        string='Rate',
        currency_field='currency_id'
    )

    project_sla_id = fields.Many2one('project.sla')
    active = fields.Boolean(string='Active', tracking=True, required=False, default=True)

    @api.depends('country_id')
    def _compute_currency_id(self):
        for record in self:
            record.currency_id = self.env.ref('base.USD').id

    @api.constrains('country_id', 'project_sla_id')
    def _check_unique_country(self):
        for record in self:
            same_country_lines = self.env['project.sla.line'].search([
                ('country_id', '=', record.country_id.id),
                ('project_sla_id', '=', record.project_sla_id.id),
                ('id', '!=', record.id)
            ])
            if same_country_lines:
                raise ValidationError("The Same Country Cannot Be Selected More Than Once!.")
