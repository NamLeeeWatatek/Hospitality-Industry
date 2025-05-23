{
    "name": "Sale Custom",
    "version": "1.0",
    "category": "Sales",
    "summary": "Custom enhancements for sales module",
    "description": "This module provides custom features and enhancements for the sales module in Odoo.",
    "author": "Minh",
    'category': 'API',
    'depends': [
        'sale',
    ],
    "data": [
        "views/sale_order_views.xml",
        # 'data/ir_model_fields.xml',
        # 'data/ir_ui_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}