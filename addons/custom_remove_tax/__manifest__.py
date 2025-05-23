{
    'name': 'Remove Tax Field in Sale Order Line and Invoice',
    'version': '1.0',
    'category': 'Inventory',
    'description': 'Module to remove tax fields from sale.order.line and account.move.line in Odoo 18',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/hidden_operations.xml'
    ],
    # 'installable': True,
    # 'auto_install': False,
    "installable": True,
    "application": True,
    'license': 'LGPL-3',
}