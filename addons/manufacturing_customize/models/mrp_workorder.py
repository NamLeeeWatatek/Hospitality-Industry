from odoo import fields, models, api
from odoo.exceptions import UserError

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def _update_raw_material_quantity(self):
        """Cập nhật quantity trong move_raw_ids dựa trên tổng consumption từ time_ids."""
        for workorder in self:
            # Nhóm time_ids theo raw_material
            consumption_by_material = {}
            for time_entry in workorder.time_ids:
                if time_entry.raw_material and time_entry.consumption:
                    material_id = time_entry.raw_material.id
                    if material_id not in consumption_by_material:
                        consumption_by_material[material_id] = 0.0
                    consumption_by_material[material_id] += time_entry.consumption

            # Cập nhật quantity trong move_raw_ids
            for move in workorder.move_raw_ids:
                # if move.state in ('done', 'cancel'):
                #     continue  # Bỏ qua các move đã hoàn tất hoặc hủy
                material_id = move.product_id.id
                if material_id in consumption_by_material:
                    move.quantity = consumption_by_material[material_id]
                # else:
                #     move.quantity = 0.0  # Đặt về 0 nếu không có tiêu thụ

    @api.depends('time_ids', 'time_ids.raw_material', 'time_ids.consumption', 'move_raw_ids')
    def _compute_raw_material_quantity(self):
        """Tính toán quantity cho move_raw_ids khi time_ids thay đổi."""
        self._update_raw_material_quantity()

    def write(self, vals):
        """Ghi đè write để cập nhật quantity khi time_ids hoặc move_raw_ids thay đổi."""
        res = super(MrpWorkorder, self).write(vals)
        self._update_raw_material_quantity()
        return res
    
    @api.depends('operation_id', 'production_id.bom_id')
    def _compute_duration_expected(self):
        for workorder in self:
            if workorder.operation_id and workorder.production_id.bom_id:
                # Lấy thời gian công đoạn từ BoM mà không nhân với số lượng
                workorder.duration_expected = workorder.operation_id.time_cycle
            # else:
            #     workorder.duration_expected = 0.0
