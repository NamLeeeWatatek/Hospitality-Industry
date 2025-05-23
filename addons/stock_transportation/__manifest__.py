{
    'name': 'Stock Transportation',
    'version': '1.0',
    'summary': 'Manage move packed consignments and home to Transit',
    'author': 'Cuong Nguyen',
    'category': 'Inventory',
    'depends': ['serialized_packages', 'vehicle_management', 'purchase_custom', 'stock', 'sale'],
    'data': [
        'data/ir_actions_act_window.xml',
        'data/ir_ui_menu.xml',
        # 'views/stock_picking_views.xml',  # File view để làm trường quantity thành read-only
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}