from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    origin = fields.Char(string='Chứng từ gốc')
    state = fields.Selection(selection_add=[('saved_quotation', 'Báo giá đã lưu')])
    lenh_san_xuat = fields.Many2many(
        'mrp.production', 
        'mrp_production_sale_order_rel', 
        string='Lệnh sản xuất'
    )
    saved_quotation = fields.Many2many(
        'sale.order', 
        'x_sale_order_sale_order_rel', 
        'sale_order_id', 
        'saved_quotation_id', 
        string='Báo giá đã lưu',
        copy=True
    )
    ma_khach_hang = fields.Char(
        related='partner_id.x_ma_khachhang', 
        string='Mã khách hàng', 
        readonly=True, 
        store=False
    )

    def action_request_approval(self):
        for order in self:
            new_order = order.copy({
                'state': 'saved_quotation',
                'origin': order.name,
            })
            order.saved_quotation = [(4, new_order.id)]

    def action_confirm(self):
        # Gọi phương thức gốc
        res = super(SaleOrder, self).action_confirm()

        if self.warehouse_id.name == "Kho thành phẩm":
            # Tạo lệnh sản xuất cho từng sản phẩm trong đơn hàng
            for line in self.order_line:
                if line.product_id:
                    # Kiểm tra BOM của sản phẩm
                    if not line.product_id.bom_ids:
                        raise UserError(f"Sản phẩm {line.product_id.name} không có BOM.")

                    # Kiểm tra tồn kho của sản phẩm trong "Kho thành phẩm"
                    stock_quant = self.env['stock.quant'].search([
                        ('product_id', '=', line.product_id.id),
                        ('location_id', '=', self.warehouse_id.lot_stock_id.id)
                    ], limit=1)

                    available_qty = stock_quant.quantity if stock_quant else 0

                    required_qty = line.product_uom_qty

                    # Nếu tồn kho không đủ, tạo lệnh sản xuất
                    if available_qty < required_qty:
                        production_qty = required_qty - available_qty
                        production = self.env['mrp.production'].create({
                            'product_id': line.product_id.id,
                            'product_qty': production_qty,
                            'product_uom_id': line.product_uom.id,
                            'bom_id': line.product_id.bom_ids[:1].id,  # Chọn BOM đầu tiên
                            'company_id': self.company_id.id,
                            'don_ban_hang': self.id,  # Ghi chú nguồn gốc đơn hàng
                        })
                        # Thêm lệnh sản xuất vừa tạo vào đơn hàng hiện tại ở bảng lenh_san_xuat
                        self.lenh_san_xuat = [(4, production.id)]

        return res