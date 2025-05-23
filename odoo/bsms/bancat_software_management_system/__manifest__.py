{
    "name": "BSMS",
    "author": "BANCAT",
    "license": "LGPL-3",
    "category": "Services",
    "depends": ["base", "contacts"],
    "data": [
        'security/ir.model.access.csv',
        'views/bsms_patient_contact_view.xml',
        'views/bsms_donor_contact_view.xml',
        'views/bsms_donor_type_view.xml',
        'views/menu_items.xml',

        #data_file

        'data/bsms_donor_type.xml',


    ],
    'demo': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
