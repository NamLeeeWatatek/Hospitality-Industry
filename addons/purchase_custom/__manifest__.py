# -*- coding: utf-8 -*-
{
    'name': 'purchase custom',
    'version': '18.0.1.0',
    'category': 'Inventory',
    'description': u"""
        Customization for Purchase
    """,
    'author': 'Cong Vo',
    'depends': [
        'purchase',
        'web_grid',
        'web_hierarchy',
        'web_studio',
        'group_permission_lp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_view_custom.xml',
        'views/purchase_order_form.xml',
        'views/purchase_order_list.xml',
        'views/purchase_warning_wizard_view.xml',
        'views/purchase_history_list.xml',
    ],
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}