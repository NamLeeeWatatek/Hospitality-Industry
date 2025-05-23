from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Field to store the file
    file_origin = fields.Binary(
        string="Tệp mới",
        copy=True
    )

    # Field to store the filename
    filename_origin = fields.Char(
        string="Tên tệp",
        copy=True
    )