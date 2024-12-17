# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    recruitment_team_id = fields.Many2one(comodel_name='hr.recruitment.team', string='Users Recruitment Team', )
