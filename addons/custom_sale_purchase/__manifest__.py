# -*- coding: utf-8 -*-
{
    'name': "custom_sale_purchase",

    'summary': "Custom sale purchase",

    'description': """
Long description of module's purpose
    """,

    'author': "Dong Hai",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['custom_stock_picking', 'custom_invoices', 'stock_product_report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/custom_purchase_product_home_form_view.xml',
        'views/purchase_order_form_readonly_rules.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

