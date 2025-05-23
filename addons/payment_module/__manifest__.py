{
    'name': 'Custom Payment Register',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Kế thừa form Account Payment Register để thêm custom field',
    'author': 'Le Duc Nam',
    'website': 'https://yourwebsite.com',
    'depends': ['account','web'],
    'data': [
        
        'views/account_payment_register_form.xml' ,
        'views/account_payment_views.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            "payment_module/static/src/js/account_payment_popover.js",
            'payment_module/static/src/views/account_payment_popover.xml',
            'payment_module/static/src/js/account_payment_field.js',
            'payment_module/static/src/views/account_payment_field.xml',
        ]
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}