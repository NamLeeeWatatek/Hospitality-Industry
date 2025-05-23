{
    'name': 'Warehouse Receipt',
    'version': '1.0',
    'summary': 'Thêm trường nhà cung cấp, kho lưu trữ và ngày nhập kho thực tế vào stock.picking',
    'category': 'Inventory',
    'author': 'Le Duc Nam',
    'depends': ['stock','auto_serial_number','custom_product','qc_stock_import','debt_report_module','invoice_due_alert','payment_module'],
    'data': [
        'views/stock_picking_views.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
