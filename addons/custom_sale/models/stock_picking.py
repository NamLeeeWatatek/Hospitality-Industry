import re
from odoo import models, fields, api
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Trường lưu tên tài xế
    ten_tai_xe = fields.Char(string="Tên tài xế")
    
    # Trường lưu thông tin chi tiết về xe
    thong_tin_xe = fields.Char(string="Thông tin xe")
    
    # Trường lưu biển số xe
    bien_so_xe = fields.Char(string="Biển số xe")

    sale_id = fields.Many2one("sale.order", string="Đơn Bán Hàng", compute="_compute_sale_order", store=True)
    button_visibility = fields.Boolean(string="Button Visibility", compute="_compute_button_visibility")

    @api.depends("origin")
    def _compute_sale_order(self):
        for record in self:
            sale_order = self.env["sale.order"].search([("name", "=", record.origin)], limit=1)
            record.sale_id = sale_order

    @api.depends("origin")
    def _compute_button_visibility(self):
        for record in self:
            origin = record.origin if isinstance(record.origin, str) else ""
            record.button_visibility = bool(re.match(r'^S\d+', origin))


    def action_return_to_sale_order(self):
        if not self.sale_id:
            raise UserError("Không tìm thấy đơn bán hàng liên quan!")
        return {
            "type": "ir.actions.act_window",
            "name": "Đơn Bán Hàng",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": self.sale_id.id,
            "target": "current",
        }