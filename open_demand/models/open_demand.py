# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SBOpenDemand(models.Model):
    _name = 'sb.open.demand'
    _description = 'SB Open Demand'
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]

    # Char/Text Fields
    name = fields.Char("Request No.", default="/", tracking=True)
    street = fields.Char("Street 1", related="worksite_id.street", store=True, tracking=True)
    street2 = fields.Char("Street 2", related="worksite_id.street2", store=True, tracking=True)
    zip = fields.Char("Zip", related="worksite_id.zip", store=True, tracking=True)
    remarks = fields.Text("Remarks SDM/Recuitment")
    remarks_logs = fields.Text("Remarks Logs SDM/Recuitment")
    days_per_week = fields.Char("Days per Week", tracking=True)
    acknowledge_delay_datetime = fields.Char(string='Acknowledge Delay', readonly=True, copy=False)
    active_delay_datetime = fields.Char(string='Active Delay', readonly=True, copy=False)
    assign_ids_delay_datetime = fields.Char(string='Assign Ids Delay', readonly=True, copy=False)
    requirement_fulfilled = fields.Char(string='Requirement Fulfilled', readonly=True, copy=False)
    rejection_in_percentage = fields.Char(string='Rejected %', readonly=True, copy=False, tracking=True,
                                          compute="_compute_application_counts",
                                          )
    onborded_in_percentage = fields.Char(string='Onborded %', readonly=True, copy=False, tracking=True,
                                         compute="_compute_application_counts",
                                         )
    initial_value = fields.Char(string='initial_value', readonly=True, copy=False, tracking=True)
    new_value = fields.Char(string='new_value', readonly=True, copy=False, tracking=True)

    # Date Fields
    assigned_date = fields.Date("Assigned Date", tracking=True)
    expected_delivery_date = fields.Date("Target date expected by Delivery Team / Client", tracking=True)
    committed_date = fields.Date("Recruitment / FSM Committed Date", tracking=True, copy=False)
    vendor_committed_date = fields.Date("Vendor Committed Date", tracking=True, copy=False)
    requirement_received_date = fields.Date("Requirement Received Date", tracking=True, copy=False)
    acknowledge_datetime = fields.Datetime(string='Acknowledge Date/Time', copy=False)
    active_datetime = fields.Datetime(string='Active Date/Time', copy=False)
    assign_ids_datetime = fields.Datetime(string='Assign Ids Date/Time', copy=False)
    profile_submit_datetime = fields.Datetime(string='ProfileSubmit Date/Time', copy=False)
    r1_datetime = fields.Datetime(string='R1Scheduled Date/Time', copy=False)
    r1done_datetime = fields.Datetime(string='R1 Done Date/Time', copy=False)
    application_pending_datetime = fields.Datetime(string='Pending From Client Date/Time', copy=False)
    client_round_done_datetime = fields.Datetime(string='client Round Done Date/Time', copy=False)

    # Boolean Fields
    is_acknowledgment = fields.Boolean("Acknowledgment", default=False, copy=False)
    is_reminder = fields.Boolean(string="Reminder", tracking=True)

    # Selection Fields
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("fulfilled", "Fulfilled"), ("hold", "Hold"), ("lost", "Lost"),
         ("descoped", "Descoped"), ],
        default="draft", tracking=True, store=True, string='Status')
    priority = fields.Selection(
        [("Urgent", "Urgent"), ("Critical", "Critical"), ("Medium", "Medium"), ("Low", "Low"), ],
        string="Priority", tracking=True, )
    global_level = fields.Selection(
        string='Level',
        selection=[('a1', 'A1'),
                   ('a2', 'A2'),
                   ('b1', 'B1'),
                   ('b2', 'B2'),
                   ('c1', 'C1'),
                   ('c2', 'C2'),
                   ('native', 'Native')])
    local_level = fields.Selection(
        string='Level',
        selection=[('a1', 'A1'),
                   ('a2', 'A2'),
                   ('b1', 'B1'),
                   ('b2', 'B2'),
                   ('c1', 'C1'),
                   ('c2', 'C2'),
                   ('native', 'Native')])
    opportunity_type = fields.Selection([("Bussiness", "Bussiness"), ("Operations", "Operations"), ],
                                        'Opportunity Type', default="Bussiness", tracking=True, )
    target_rate_duration = fields.Selection(
        [("FullDay", "Full Day"), ("HalfDay", "Half Day"), ("Monthly", "Monthly"), ("Hourly", "Hourly"), ],
        "Target Rate Duration", tracking=True, )

    # Integer Fields
    required_quantity = fields.Integer("Required Quantity", tracking=True, )
    application_received = fields.Integer(
        "Profiles Received Qty.(FSM & Recr.)",
        tracking=True,
        compute="_compute_application_counts")
    application_first_review = fields.Integer(
        "R1 Scheduled", tracking=True,
        compute="_compute_application_counts")
    application_first_done_review = fields.Integer(
        "R1 Done", tracking=True,
        compute="_compute_application_counts")
    application_pending = fields.Integer(
        "Pending with Customer", tracking=True,
        compute="_compute_application_counts")
    application_client_done = fields.Integer(
        "Client round done", tracking=True,
        compute="_compute_application_counts")
    application_rejected = fields.Integer(
        "Rejected / Backed Out Qty. / Unavailable",
        tracking=True,
        compute="_compute_application_counts")
    application_selected = fields.Integer(
        "Selected / Onboarded", tracking=True,
        compute="_compute_application_counts")
    balance = fields.Integer(
        "Balance", store=True, tracking=True)
    applicant_count = fields.Integer(string='Applicant Count', compute='_compute_applicant_count')

    # Float Fields
    target_rate = fields.Float("Target Rate", tracking=True)
    max_target_rate = fields.Float("Maximum Target Rate", tracking=True)
    probability = fields.Float('Probability', group_operator="avg", copy=False, readonly=False, store=True)

    # Other Fields
    expected_revenue = fields.Monetary('Expected Revenue', tracking=True)
    job_description = fields.Html("Job Description", required=True)


    # Many2one Fields
    skill_id = fields.Many2one(string='Skillset',comodel_name='project.skill', ondelete='cascade')
    worksite_id = fields.Many2one(
        "project.worksite", "Worksite", tracking=True, domain="[('id', 'in', worksite_ids)]")
    currency_id = fields.Many2one("res.currency", string="Currency", tracking=True)
    owner_team_ids = fields.Many2one("hr.recruitment.team", "Owner Team")
    sdm_team_ids = fields.Many2one("hr.recruitment.team", "SDM Team")
    local_language_id = fields.Many2one("res.lang", "Local Language", tracking=True)
    language_id = fields.Many2one("res.lang", "Language", tracking=True)
    client_poc_id = fields.Many2one("res.users", "Client POC", tracking=True)
    country_id = fields.Many2one(
        "rate.country", "Country", tracking=True, related="worksite_id.country_id", store=True)
    city_id = fields.Many2one(
        "rate.city", "City", tracking=True, related="worksite_id.city_id", store=True)
    region_id = fields.Many2one(
        "rate.region", "Region", tracking=True, related="worksite_id.region_id", store=True)
    client_id = fields.Many2one("res.partner", "Client", domain="[('type','=','contact')]", tracking=True)
    project_id = fields.Many2one(
        "project.project", "Project", domain="[('partner_id','=',client_id)]", tracking=True)
    resource_type_id = fields.Many2one(comodel_name="service.type",  string="Resource Type")

    # Many2many Fields
    applicant_ids = fields.Many2many(comodel_name='hr.applicant', relation='hr_applicant_sb_open_demand_rel',
                                     column1='sb_open_demand_id', column2='hr_applicant_id', string='Applicants',
                                     tracking=True)
    worksite_ids = fields.Many2many(
        'project.worksite', compute="_compute_worksite_ids", store=False, string="Related Worksites"
    )
    assign_ids = fields.Many2many("res.users", string="Current Owner", tracking=True, copy=False)

    # Method
    @api.onchange('project_id')
    def _compute_worksite_ids(self):
        """
        This method is triggered when the user selects or changes the project (project_id)
        on the form. It updates the available options for the 'worksite_id' field based on
        the tasks linked to the selected project.

        Why we use @api.onchange:
        - The @api.onchange decorator is used to detect when the project_id field changes.
        - It allows us to dynamically update the form in real-time, before the record is saved.
        - This gives the user immediate feedback and updates the list of available worksites.

        Effect:
        - When the user selects a project, this method fetches all tasks related to that project.
        - It then extracts the worksites from those tasks.
        - The 'worksite_id' field is then updated to show only worksites linked to the selected project.
        """
        for record in self:
            if record.project_id:
                # Get all tasks related to the selected project
                tasks = self.env['project.task'].search([('project_id', '=', record.project_id.id)])
                # Extract worksites from those tasks
                worksites = tasks.mapped('worksite_id')
                record.worksite_ids = worksites
            else:
                # If no project is selected, clear the worksites
                record.worksite_ids = False
    # Onchange Method
    @api.onchange('worksite_id')
    def _onchange_fields_from_task(self):
        """
        This method is triggered when the worksite_id is selected/changed.
        It fetches resource_type_id and skill_id from the project.task model.
        """
        for rec in self:
            if rec.worksite_id:
                # Search for tasks that are related to the selected worksite_id
                tasks = self.env['project.task'].search([('worksite_id', '=', rec.worksite_id.id)], limit=1)

                if tasks:
                    task = tasks[0]
                    rec.resource_type_id = task.service_type_id
                    rec.skill_id = task.skill_id
                    rec.job_description = task.job_description
                else:
                    rec.resource_type_id = False
                    rec.skill_id = False
                    rec.job_description = False
            else:
                rec.resource_type_id = False
                rec.skill_id = False
                rec.job_description = False

    # Compute Methods
    def _compute_applicant_count(self):
        for open_demnad in self:
            open_demnad.applicant_count = self.env['hr.applicant'].search_count([('demand_ids', 'in', open_demnad.ids)])

    def write(self, values):
        result = super(SBOpenDemand, self).write(values)
        return result

    def set_active(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'active'
                rec.name = str(rec.id).zfill(6)

    def set_hold(self):
        for rec in self:
            # if rec.state == 'active':
            rec.state = 'hold'

    def set_fulfilled(self):
        return {
            'name': 'Requirement Fulfilled',
            'type': 'ir.actions.act_window',
            'res_model': 'requirement.fulfilled.wizard',  # Replace with the actual wizard model name
            'view_mode': 'form',
            'target': 'new',
        }

    def set_cancel(self):
        for rec in self:
            # if rec.state == 'active':
            rec.state = 'descoped'

    def set_lost(self):
        for rec in self:
            # if rec.state == 'active':
            rec.state = 'lost'

    def action_view_applicants(self):
        self.ensure_one()
        tree_view_id = self.env.ref('hr_recruitment_ext.hr_applicant_view_tree').id
        form_view_id = self.env.ref('hr_recruitment_ext.hr_applicant_view_form_inherit').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Applicants',
            'view_mode': 'tree,form',
            'view': [
                (tree_view_id, 'tree'),
                (form_view_id, 'form')
            ],
            'res_model': 'hr.applicant',
            'domain': [('demand_ids', 'in', self.ids)]
        }

    @api.depends('applicant_ids.stage_id')
    def _compute_application_counts(self):
        for record in self:
            # R1 Scheduled applicant Count
            application_first_review_count = self.env['hr.applicant'].search_count([
                ('id', 'in', record.applicant_ids.ids),
                ('stage_id.name', '=', 'R1 Scheduled')
            ])

            # R1 Done
            application_first_done_review_count = self.env['hr.applicant'].search_count([
                ('id', 'in', record.applicant_ids.ids),
                ('stage_id.name', '=', 'R1 Done')
            ])
            # Pending with Customer
            application_pending_count = self.env['hr.applicant'].search_count([
                ('id', 'in', record.applicant_ids.ids),
                ('stage_id.name', '=', 'Pending with Customer')
            ])
            # Client Round Done
            application_client_done_count = self.env['hr.applicant'].search_count([
                ('id', 'in', record.applicant_ids.ids),
                ('stage_id.name', '=', 'Client Round Done')
            ])
            # Rejected or Backoff
            application_rejected_count = self.env['hr.applicant'].search_count([
                ('id', 'in', record.applicant_ids.ids),
                ('stage_id.name', '=', 'Rejected or Backoff')
            ])
            # Contract Signed & Onboarded
            application_selected_count = self.env['hr.applicant'].search_count([
                ('id', 'in', record.applicant_ids.ids),
                ('stage_id.name', '=', 'Contract Signed & Onboarded')
            ])

            # Set the counts in the respective fields
            record.application_received = len(record.applicant_ids)
            record.application_first_review = application_first_review_count
            record.application_first_done_review = application_first_done_review_count
            record.application_pending = application_pending_count
            record.application_client_done = application_client_done_count
            record.application_rejected = application_rejected_count
            record.application_selected = application_selected_count
            if len(record.applicant_ids) > 0.0:
                record.rejection_in_percentage = (application_rejected_count / len(record.applicant_ids)) * 100
                record.onborded_in_percentage = (application_selected_count / len(record.applicant_ids)) * 100
            else:
                record.rejection_in_percentage = 0
                record.onborded_in_percentage = 0

            if application_pending_count > 0:
                if record.sdm_team_ids and record.sdm_team_ids.user_id:
                    record.assign_ids = record.sdm_team_ids.user_id.ids
