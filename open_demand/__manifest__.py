# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Open Demand",
    'version': '17.0.1.0.2',
    'author': 'Hasnain Taqi Kazmi',
    'summary': "This module extends the functionalities of the Rate Card.",
    'category': 'Human Resources/Employees',
    'sequence': 10,

    'depends': ['base_setup', 'mail', 'rate_card', 'website_hr_recruitment', ], # 'phone_validation',
    'data': [
        'security/ir.model.access.csv',
        'views/open_demand_views.xml',
        'views/open_demand_reporting_views.xml',
        'views/hr_recruitment_team_views.xml',
        'views/menus.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'license': 'OEEL-1',

}
