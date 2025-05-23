# -*- coding: utf-8 -*-
{
    'name': "custom_invoices",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Nam Le",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','consignment','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/custom_purchase_invoice_view.xml',
        'views/custom_invoice_consignment_filter.xml',
        'views/custom_invoice_consignment_form_view.xml',
        'views/custom_invoice_purchase_list.xml',
        'views/custom_invoice_purchase_filter.xml',
        'reports/invoice_non_payment.xml',
        'views/custom_view_account_payment_tree.xml',
        'views/custom_invoice_form_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

