{
    "name": "Long Phuong User Groups",
    "version": "1.0",
    "depends": ["base", 'stock_transportation', 'custom_sale_purchase', 'warehouse_receipt'],
    "author": "Cuong Nguyen",
    "category": "Inventory",
    "description": "Create Long Phượng user groups on module installation",
    "installable": True,
    "auto_install": False,
    "pre_init_hook": "pre_init_create_user_groups",
    "license": "LGPL-3",
}