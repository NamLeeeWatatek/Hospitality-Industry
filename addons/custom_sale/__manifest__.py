{
    "name": "Custom Sale",
    "version": "1.0",
    "summary": "Customize sale order",
    "author": "Cuong Nguyen",
    "category": "Inventory",
    "depends": ["sale", "stock", "account", "base"],
    "data": [
        "views/sale_order_form_view.xml",
        "views/product_uom_id_view.xml",
        "views/sale_report_search.xml",
        "views/custom_sale_report_consignment_list_view.xml",
        "views/consignment_stock_delivery_CAM_filter.xml",
        "views/consignment_stock_receipt_CAM_filter.xml",
        "views/ir_actions_act_window.xml",
        "views/ir_ui_view.xml",
        "data/ir_ui_menu.xml",
        "views/custom_stock_picking.xml",
        "views/sale_order_action.xml",
        "views/stock_picking_list_home_product_order.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "custom_sale/static/src/js/stock_report_search_panel.js",
        ]
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
