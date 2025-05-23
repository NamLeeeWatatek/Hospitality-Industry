{
    'name': 'License',
    'version': '1.0.0',
    'sequence': -50,
    'author': 'WATATEK',
    'website': 'www.watatek.com',
    'category': 'API',
    'summary': 'License',
    'description': 'License',
    'depends': ['base'],
    'data': [
        'data/schedule_rule.xml',
        'security/ir.model.access.csv',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}