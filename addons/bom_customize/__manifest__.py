{
    'name': 'BoM customizations',
    'version': '1.0',
    'summary': 'BoM customizations',
    'category': 'API',
    'depends': [
        'mrp',
    ],
    'data': [
        'views/mrp_bom_custom_views.xml',  # Add the new custom views XML file
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}