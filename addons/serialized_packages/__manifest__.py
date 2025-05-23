{
    'name': 'Serialized Packages',
    'version': '1.0',
    'summary': 'Manage packed item support shipments',
    'author': 'Cuong Nguyen',
    'category': 'Inventory',
    'depends': ['consignment'],
    'data': [
        'views/transit_wizard_form.xml',
        'data/ir_actions_transit.xml',
        'views/stock_quant_consignment_list.xml',
        'views/stock_quant_home_list.xml',
        'views/delivery_stock_quant_home_list.xml',
        'views/delivery_stock_quant_consignment_list.xml',
        'views/stock_picking_views.xml',
        'data/ir_actions_act_window.xml',
        'data/ir_ui_menu.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}