from odoo import api, fields, models, _

class ProjectProject(models.Model):
    _inherit = "project.project"

    name = fields.Char("Name", index='trigram', required=True, tracking=True, translate=True,
                       default_export_compatible=True, related="sale_order_id.project_name")
