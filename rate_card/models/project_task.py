from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]
    _description = 'Project Task'


    worksite_id = fields.Many2one(
        string='WorkSite',
        comodel_name='project.worksite',
        ondelete='cascade',related='sale_line_id.worksite_id'
    )


    country_id = fields.Many2one(
        comodel_name='rate.country',
        string='country',
        related='sale_line_id.country_id',
        help="Countries linked to the WorkSite associated with this task."
    )
    region_id = fields.Many2one(
        comodel_name='rate.region',
        string='region',
        related='sale_line_id.rate_region_id',
        help="Regions linked to the WorkSite associated with this task."
    )
    city_id = fields.Many2one(
        comodel_name='rate.city',
        string='city',
        related='sale_line_id.city_id',
        help="Cities linked to the WorkSite associated with this task."
    )

    street = fields.Char(related='worksite_id.street')
    street2 = fields.Char(related='worksite_id.street2')
    zip = fields.Char(change_default=True, related='worksite_id.zip')

    country_ids = fields.Many2many(
        comodel_name='rate.country',
        string='Country',
        related='sale_order_id.country_ids',
        help="Countries linked to the Sale Order associated with this task."
    )
    region_ids = fields.Many2many(
        comodel_name='rate.region',
        string='Region',
        related='sale_order_id.region_ids',
        help="Regions linked to the Sale Order associated with this task."
    )
    city_ids = fields.Many2many(
        comodel_name='rate.city',
        string='City',
        related='sale_order_id.city_ids',
        help="Cities linked to the Sale Order associated with this task."
    )
    skill_id = fields.Many2one(
        string='Skillset',
        comodel_name='project.skill',
        related='sale_line_id.skill_id',
        ondelete='cascade',
    )
    sla_ids = fields.Many2many(
        string='SLAs Type',
        comodel_name='project.sla',
        related='sale_order_id.sla_ids',
    )

    service_type_id = fields.Many2one(
        string='SLA',
        comodel_name='service.type',
        related='sale_line_id.svc_type_id',
        ondelete='cascade',
    )

    with_sla = fields.Boolean(string='SLA Enabled', tracking=True, required=False,
                              related="sale_line_id.svc_type_id.with_sla")
    out_of_office = fields.Float(
        string='Include OOH',
        required=False,
        related="sale_line_id.out_of_office",
    )
    holiday = fields.Float(
        string='Include Holiday',
        required=False,
        related="sale_line_id.holiday"
    )

    svc_desc = fields.Char(string='Service Description', related='sale_line_id.svc_desc')

    sla_id = fields.Many2one(
        string='sla type',
        comodel_name='project.sla',
        related='sale_line_id.sla_id',
    )
    price_unit = fields.Float('Unit Price', related='sale_line_id.price_unit')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  related='sale_line_id.currency_id',
                                  readonly=True)
    worksite_travel_cost = fields.Monetary(
        string='Travel Cost',
        currency_field='currency_id',
        required=False, related='sale_line_id.worksite_travel_cost'
    )
    
    # Assignment Fields
    assigned_worker_id = fields.Many2one(string="Primary Engineer", comodel_name="hr.employee", )

    backfill_engineer_id = fields.Many2one(string="Backfill Engineer", comodel_name="hr.employee", )

    secondary_backfill_id = fields.Many2one(string="Secondary Backfill Engineer", comodel_name="hr.employee", )

    service_order_source = fields.Selection(selection=[('opportunity', 'Opportunity'), ('ticket', 'Ticket')],
                                            default='opportunity',
                                            string="Source")
    opportunity_id = fields.Many2one(string="Opportunity", comodel_name="crm.lead", )
    ticket_id = fields.Many2one(string="Helpdesk Ticket", comodel_name="helpdesk.ticket", )

    # Schedule Details Fields
    tz_offset = fields.Char(string="Work-Site Timezone", )
    start_at = fields.Datetime(string="Starting At (Work-Site)", default=fields.datetime.now(), readonly=False,
                               store=True, )
    end_at = fields.Datetime(string="Ending At (Work-Site)", default=fields.datetime.now(), readonly=False, store=True, )

    job_description = fields.Html(string='Job Description', sanitize_attributes=False,
                                  related="sale_order_id.order_line.job_description",readonly=False, store=True,)
    language_ids = fields.Many2many(
        comodel_name='res.lang',
        relation='project_task_res_lang_rel',
        column1='country_id',
        column2='lang_id',
        related="sale_order_id.order_line.language_ids",
        string='Languages'
    )
    global_level = fields.Selection(
        string='Global Level',
        selection=[('a1', 'A1'),
                   ('a2', 'A2'),
                   ('b1', 'B1'),
                   ('b2', 'B2'),
                   ('c1', 'C1'),
                   ('c2', 'C2'),
                   ('native', 'Native')])
    local_level = fields.Selection(
        string='Local Level',
        selection=[('a1', 'A1'),
                   ('a2', 'A2'),
                   ('b1', 'B1'),
                   ('b2', 'B2'),
                   ('c1', 'C1'),
                   ('c2', 'C2'),
                   ('native', 'Native')])
