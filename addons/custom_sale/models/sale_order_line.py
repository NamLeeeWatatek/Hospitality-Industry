from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    consignment_packed_type = fields.Char(string="Quy cách")
    unit_of_measure = fields.Char(string="Đơn vị tính")