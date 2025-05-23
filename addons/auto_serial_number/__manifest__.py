{
    'name': "Auto Generate Serial Number",
    'version': '1.0',
    'summary': "Automatically generate serial numbers for stock moves",
    'description': """
        Module to auto-generate serial numbers for incoming stock moves.
        The serial number follows the structure: [Picking Name]-[Line Number]-[Sequence Number].
        Example: HNNCP/IN/00013-1-0000001.
    """,
    'category': 'Inventory',
    'author': "Ha Binh",
    'depends': [
        'stock', 
        'base', 
        'stock_quantity_restriction',
        'stock',
        'web_grid',
        'web_hierarchy',
        'web_studio',
        'custom_sale'
        ],  # Thêm 'base' để hỗ trợ res.config.settings
    'data': [
        'data/ir_ui_view.xml',
        'views/inherit_stock_move_line_operations_list.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}