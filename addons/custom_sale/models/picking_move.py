from odoo import models, fields

class StockMove(models.Model):
    _inherit = 'stock.move'

    consignment_packed_type = fields.Char(string="Quy cách")
    unit_of_measure = fields.Char(string="Đơn vị tính")