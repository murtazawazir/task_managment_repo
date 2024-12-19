# -*- coding: utf-8 -*-
{
    'name': "Sale Policy",

    'summary': "this module is all about sale policy",

    'description': """
this module is all about sale policy
    """,

    'author': "Murtaza Alam",

    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_policy.xml',
        'views/price_list_customization.xml',

        'wizard/wizard.xml',
        'wizard/update_policy.xml',


    ],

}
