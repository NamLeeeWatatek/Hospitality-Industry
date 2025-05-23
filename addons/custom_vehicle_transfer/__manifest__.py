{
    'name': "Vehicle Transfer",
    'version': '1.0',
    'depends': ['consignment', 'serialized_packages', 'sale_stock', 'payment_module'],
    'author': "Wata",
    'category': 'Custom',
    'description': """
    Module to manage vehicle transfer records and print PDF reports.
    """,
    'data': [
        'data/report_paperformat_data.xml',
        'security/ir.model.access.csv',
        'wizards/vehicle_transfer_wizard_views.xml',
        'views/vehicle_transfer_views.xml',
        'views/vehicle_transfer_templates.xml',
        'views/received_transfer_views.xml',
        'views/received_transfer_templates.xml',
        'views/deliveried_transfer_views.xml',
        'views/deliveried_transfer_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}