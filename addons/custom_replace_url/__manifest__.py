{
    "name": "Url Replace",
    'version': '1.0',
    "summary": "URL Replace",
    "description":"Replace odoo in hyperlink",
    "category": "Extra Tools",
    "depends": ["web",'base'],
    "application": False,
    "installable": True,
    "data": [
          'data/ir_config_parameter.xml',
          'views/ir_config_parameter_views.xml'
      ],
    "assets": {
        "web.assets_backend": [
            "custom_replace_url/static/src/**/*",
        ],
    },
    'uninstall_hook': '_uninstall_cleanup',
}