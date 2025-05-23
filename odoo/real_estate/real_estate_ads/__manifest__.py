{
    "name": "Real Estate Ads",
    "author": "CLAREx",
    "license": "LGPL-3",
    "category": "Sales",
    "depends": ["base"],
    "data": [

        "security/ir.model.access.csv",
        'views/property_view.xml',
        'views/property_type_view.xml',
        'views/property_tag_view.xml',
        'views/property_offer_view.xml',
        'views/menu_items.xml',

        #Data File
        # 'data/property_type.xml'
        'data/estate.property.type.csv',

    ],
    'demo': [
        'demo/property_tag.xml'
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
