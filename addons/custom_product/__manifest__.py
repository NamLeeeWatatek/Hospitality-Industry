{
    'name': 'custom product',
    'version': '1.0',
    'summary': 'Customize product',
    'author': ['Cong Vo', 'Vy'],
    'category': 'Inventory',
    'depends': ['base', 'product','sale'],
    'assets': {
    'web.assets_backend': [
        '/custom_product/static/src/css/custom_style.css',
        ],
    },
    'data': [
        'views/product_form_view.xml',
        'views/product_view.xml',
        'views/sale_order_views.xml',
        'views/product_form_only_view.xml',
        'views/product_template_kanban_view.xml',
        'views/product_template_tree_view.xml',
        'views/custom_product_normal_form_view.xml'
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}