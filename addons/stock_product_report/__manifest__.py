{
    'name': 'Stock Product Report',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Custom reports for Owned and Consignment Products',
    'description': """
        This module provides custom reports for 'Hàng nhà' and 'Hàng ký gửi' based on product and stock data.
    """,
    'author': 'Your Name',
    'depends': ['stock', 'product','sale','custom_product'],
    'data': [
        'views/stock_report_views.xml',
        'views/custom_stock_report_home_product_view.xml',
        'views/custom_home_product_filter.xml',
        'views/custom_consignment_product_filter.xml'
            ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}