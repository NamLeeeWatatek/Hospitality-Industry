# -*- coding: utf-8 -*-
{
    'name': 'Studio customizations',
    'version': '18.0.1.0',
    'category': 'API',
    'description': u"""
This module has been generated by Odoo Studio.
It contains the apps created with Studio and the customizations of existing apps.
""",
    'author': 'Watatek',
    'depends': [
        'purchase',
        'sale',
        'web_grid',
        'web_hierarchy',
        'web_studio',
    ],
    'data': [
        'data/ir_model_fields.xml',
        'data/ir_ui_view.xml',
        'data/ir_default.xml',
        
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
