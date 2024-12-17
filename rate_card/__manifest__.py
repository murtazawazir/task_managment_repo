# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Rate Card',
    'version': '17.0.1.0.1',
    'author': 'Hasnain Taqi Kazmi',
    'summary': 'Rate Card for Customer based on Country etc',
    'sequence': 2,
    'description': """
        Custom Module Designed for the SharpBrains:
        - Added Region model and its view.
        - Added Country model and its view.
        - Added City model and its view.
        - Added SLA model and its view.
        - Added Skill model and its view.
        - Added Worksite model and its view.
        - Added Rate model and its view.
        - Added Service type model and its view.
        - Added Service type line model and its view.
        - Inherite Sales Order model and its view.
        - Added Region, Country, City, SLA, Service Type and Skill fields in Sales Order.
        - Added Submit Button to load order_lines in Sales Order based on selected values.
    """,
    'category': 'Sales/Sales',
    'depends': ['sale_order_revision', 'crm', 'project', 'sale_project', 'helpdesk', 'website_hr_recruitment', 'mail','hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'security/sale_security.xml',
        'data/sequence.xml',
        'data/product_data.xml',
        'views/crm_lead_views_ext.xml',
        'views/rate_region_views.xml',
        'views/rate_country_views.xml',
        'views/rate_city_views.xml',
        'views/project_sla_views.xml',
        'views/project_skill_views.xml',
        'views/project_worksite_views.xml',
        'views/project_project_rate_views.xml',
        'views/sale_order_views.xml',
        'views/service_type_views.xml',
        'views/service_type_line_views.xml',
        'views/rate_card_menus.xml',
        'views/res_config_settings_view.xml',
        'views/sale_order_discount_views.xml',
        'views/project_task_views.xml',
        'views/project_views.xml',
        'wizard/rate_card_country_wizard_views.xml',
    ],
    # 'demo': [
    #     'demo/rate.region.csv',
    #     'demo/rate.country.csv',
    #     'demo/rate.city.csv',
    # ],
    'installable': True,
    'application': False,
    'license': 'OEEL-1',
}
