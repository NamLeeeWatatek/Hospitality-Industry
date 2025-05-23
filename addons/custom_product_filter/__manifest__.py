# custom_product_filter/__manifest__.py
{
    'name': "Custom Product Filter",
    'version': '18.0.1.0.0',
    'summary': "Filter products by House and Consignment types",
    'description': """
        This module allows filtering products into 'House Products' and 'Consignment Products' with a dropdown menu.
    """,
    'category': 'Inventory',
    'author': "Ha Binh",
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'data/menu_data.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}


