# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentTeam(models.Model):
    _name = "hr.recruitment.team"
    _description = "Recruitment Team"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _order = "sequence"
    _check_company_auto = True

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    name = fields.Char("Recruitment Team")

    sequence = fields.Integer("Sequence", default=10)
    active = fields.Boolean(
        default=True,
        help="If the active field is set to false, it will allow you to hide the Sales Team without removing it.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one("res.users", string="Team Leader", check_company=True)
    # memberships
    member_ids = fields.One2many(
        "res.users",
        "recruitment_team_id",
        string="Team Members",
        check_company=True,
        domain=[("share", "=", False)],
        help="Add members to automatically assign their documents to this sales team. You can only be member of one team.",
    )
    # UX options
    color = fields.Integer(string="Color Index", help="The color of the team")
    favorite_user_ids = fields.Many2many(
        "res.users",
        "recruitment_team_user_rel",
        "team_id",
        "user_id",
        string="Favorite Members",
        default=_get_default_favorite_user_ids,
    )
    is_favorite = fields.Boolean(
        string="Show on dashboard",
        compute="_compute_is_favorite",
        inverse="_inverse_is_favorite",
        help="Favorite teams to display them in the dashboard and access them easily.",
    )
    dashboard_button_name = fields.Char(
        string="Dashboard Button", compute="_compute_dashboard_button_name"
    )
    dashboard_graph_data = fields.Text(compute="_compute_dashboard_graph")

    # CRUD Functions
    @api.model_create_multi
    def create(self, vals_list):
        team = super(HrRecruitmentTeam, self.with_context(mail_create_nosubscribe=True)).create(vals_list)
        for vals in vals_list:
            if vals.get("member_ids"):
                team._add_members_to_favorites()
        return team

    def write(self, vals):
        res = super(HrRecruitmentTeam, self).write(vals)
        if vals.get("member_ids"):
            self._add_members_to_favorites()
        return res


    def _compute_is_favorite(self):
        for team in self:
            team.is_favorite = self.env.user in team.favorite_user_ids


    def _inverse_is_favorite(self):
        sudoed_self = self.sudo()
        to_fav = sudoed_self.filtered(
            lambda team: self.env.user not in team.favorite_user_ids
        )
        to_fav.write({"favorite_user_ids": [(4, self.env.uid)]})
        (sudoed_self - to_fav).write({"favorite_user_ids": [(3, self.env.uid)]})
        return True


    def _add_members_to_favorites(self):
        for team in self:
            team.favorite_user_ids = [(4, member.id) for member in team.member_ids]
