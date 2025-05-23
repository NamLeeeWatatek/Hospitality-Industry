from odoo import fields, models, api
from odoo.exceptions import UserError

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    so_met_ng = fields.Float(string='Số mét NG', store=True)
    request_materials = fields.One2many(
        'request.materials',  # Model liên kết
        'workorder_id',       # Trường Many2one trong model liên kết
        string='Lịch sử sử dụng nguyên liệu',  # Nhãn hiển thị
        copy=True             # Cho phép sao chép dữ liệu khi sao chép bản ghi
    )

    def call_iqc(self):
        test_type_id = self.env['quality.point.test_type'].search([('name', 'ilike', 'Đạt - Không đạt')], limit=1)
        if not test_type_id:
            raise UserError("Không tìm thấy loại kiểm tra 'Đạt - Không đạt'.")

        team_id = self.env['quality.alert.team'].search([('name', 'ilike', 'IQC')], limit=1)
        if not team_id:
            raise UserError("Không tìm thấy nhóm kiểm tra 'IQC'.")

        self.env['quality.check'].create({
            'workorder_id': self.id,
            'team_id': team_id.id,
            'test_type_id': test_type_id.id,
            'product_id': self.product_id.id,
            'production_id': self.production_id.id,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công!',
                'message': f"Đã tạo phiếu kiểm tra IQC cho lệnh sản xuất {self.production_id.name}.",
                'type': 'success',  # Loại thông báo: success, warning, danger
                'sticky': False,    # Thông báo tự động ẩn sau vài giây
            },
        }
    def call_pqc(self):
        test_type_id = self.env['quality.point.test_type'].search([('name', 'ilike', 'Đạt - Không đạt')], limit=1)
        if not test_type_id:
            raise UserError("Không tìm thấy loại kiểm tra 'Đạt - Không đạt'.")

        team_id = self.env['quality.alert.team'].search([('name', 'ilike', 'PQC')], limit=1)
        if not team_id:
            raise UserError("Không tìm thấy nhóm kiểm tra 'PQC'.")

        self.env['quality.check'].create({
            'workorder_id': self.id,
            'team_id': team_id.id,
            'test_type_id': test_type_id.id,
            'product_id': self.product_id.id,
            'production_id': self.production_id.id,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công!',
                'message': f"Đã tạo phiếu kiểm tra PQC cho lệnh sản xuất {self.production_id.name}.",
                'type': 'success',  # Loại thông báo: success, warning, danger
                'sticky': False,    # Thông báo tự động ẩn sau vài giây
            },
        }