{
    'name': 'Request materials',
    'version': '1.0',
    'summary': 'Request materials',
    'category': 'API',
    'depends': [
        'mrp',
    ],
    'data': [
        'security/request_materials_security.xml',
        'views/mrp_production_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}