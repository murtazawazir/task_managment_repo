from odoo import models, api, fields


class CRMLeadExt(models.Model):
    _inherit = 'crm.lead'

    sla_ids = fields.Many2many(
        string='SLAs',
        comodel_name='project.sla',
        relation='sla_crm_rel',
        column1='sla_id',
        column2='crm_id',
    )

    service_type_ids = fields.Many2many(
        string='Service Type',
        comodel_name='service.type',
        relation='service_type_crm_rel',
        column1='service_type_id',
        column2='service_type_crm_id',
    )