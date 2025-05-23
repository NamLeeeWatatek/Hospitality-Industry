from odoo import fields, models, api
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    hao_phi = fields.Float(
        string="Hao phí",
        copy=True,
        store=True,
        default=0.0,
    )

    calculated_raw_qty = fields.Float(
        string="Số lượng nguyên liệu cần dùng",
        compute="_compute_calculated_raw_qty",
        store=True,  # Không lưu trữ vì là trường tính toán
        help="Số lượng nguyên liệu tính toán dựa trên BoM và lệnh sản xuất"
    )

    @api.depends('bom_line_id', 'raw_material_production_id.product_qty')
    @api.onchange('bom_line_id', 'raw_material_production_id.product_qty')
    def _compute_calculated_raw_qty(self):
        for move in self:
            if move.bom_line_id and move.raw_material_production_id:
                bom_line = move.bom_line_id
                bom = bom_line.bom_id
                production = move.raw_material_production_id
                if bom.product_qty > 0:  # Tránh chia cho 0
                    move.calculated_raw_qty = (bom_line.product_qty / bom.product_qty) * production.product_qty
                else:
                    move.calculated_raw_qty = 0.0
            else:
                move.calculated_raw_qty = 0.0
            move._update_product_uom_qty()

    @api.constrains('hao_phi')
    def _check_hao_phi(self):
        for move in self:
            if move.hao_phi < 0:
                raise ValidationError("Hao phí không thể âm!")

    @api.depends('calculated_raw_qty', 'hao_phi')
    @api.onchange('calculated_raw_qty', 'hao_phi')
    def _update_product_uom_qty(self):
        """Hàm riêng để cập nhật product_uom_qty dựa trên calculated_raw_qty và hao_phi"""
        for move in self:
            if move.calculated_raw_qty > 0:
                hao_phi_factor = 1 + move.hao_phi  # Chuyển hao_phi thành hệ số (ví dụ: 10% -> 1.1)
                move.product_uom_qty = move.calculated_raw_qty * hao_phi_factor
            # else:
            #     move.product_uom_qty = 0.0