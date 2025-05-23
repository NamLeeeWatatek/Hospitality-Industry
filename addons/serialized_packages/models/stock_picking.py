from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ten_tai_xe = fields.Char(string="Tên tài xế")
    thong_tin_xe = fields.Char(string="Thông tin xe")
    bien_so_xe = fields.Char(string="Biển số xe")
    is_transit_out = fields.Boolean(string="Xuất kho ký gửi", default=False)