{
    'name': "Vehicle Management",
    'version': '1.0',
    'summary': "Module quản lý xe",
    'description': """Module quản lý xe với các tính năng:
                     - Tạo mới và chỉnh sửa thông tin xe
                     - Tìm kiếm và lọc xe theo biển số xe
                     - Quản lý trạng thái hoạt động của xe
                     - Hiển thị danh sách mã số xe""",
    'author': "Ha Binh",
    'category': 'Inventory',
    'depends': ['base', 'stock_quantity_restriction', 'auto_serial_number', 'custom_product_filter', 'custom_remove_tax'],
    'data': [
        'security/ir.model.access.csv',
        'security/vehicle_management_security.xml',
        'views/vehicle_views.xml',  
        'views/vehicle_menu.xml',   
        'views/vehicle_status_history_views.xml',
        'wizards/vehicle_status_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
