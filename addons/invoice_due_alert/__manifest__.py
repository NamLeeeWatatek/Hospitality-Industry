{
    'name': 'Invoice Due Alert',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Thông báo công nợ quá hạn trong Odoo',
    'depends': ['account', 'bus'],
    'data': [
        'views/account_move_views.xml',
        'views/scheduled_action.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
