from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpWorkorderRawsConsumed(models.Model):
    _name = 'request.materials'
    _description = 'Lịch sử bổ sung nguyên liệu'

    workorder_id = fields.Many2one(
        'mrp.workorder', 
        string='Công đoạn', 
        required=True, 
        ondelete='cascade'
    )
    raw_material = fields.Many2one(
        'product.product',
        string="Nguyên liệu",
        domain="[('id', 'in', allowed_raw_material_ids)]"
    )
    worker_id = fields.Many2one(
        'hr.employee', 
        string='Công nhân', 
        required=True
    )
    quantity_by_material = fields.Float(
        string='Số lượng tiêu thụ', 
        digits='Product Unit of Measure', 
        required=True
    )
    date = fields.Datetime(
        string='Ngày sử dụng', 
        default=fields.Datetime.now, 
        required=True
    )
    list_error = fields.Selection(
        [('0', 'Không có lỗi'), ('1', 'Thiếu nguyên liệu'), ('2', 'Sai nguyên liệu')],
        string='Lỗi',
        default='0',
    )
    text_error = fields.Text(
        string='Nội dung lỗi',
        required=False
    )
    status = fields.Boolean(
        string='Phê duyệt',
        default=False
    )
    allowed_raw_material_ids = fields.Many2many(
        'product.product',
        compute="_compute_allowed_raw_material_ids",
        store=False
    )
    @api.depends('workorder_id')
    def _compute_allowed_raw_material_ids(self):
        for record in self:
            if record.workorder_id:
                record.allowed_raw_material_ids = record.workorder_id.move_raw_ids.mapped('product_id')
    
    def approve_request(self):
        # Tìm loại phiếu giao nguyên liệu
        picking_type = self.env['stock.picking.type'].search([('name', '=', 'Phiếu giao nguyên liệu')], limit=1)
        if not picking_type:
            raise UserError("Không tìm thấy loại phiếu 'Phiếu giao nguyên liệu'.")
        self.status = True
        # Tạo phiếu giao nguyên liệu
        location_src = picking_type.default_location_src_id
        location_dest = picking_type.default_location_dest_id
        partner = self.env.user.partner_id

        new_picking = self.env['stock.picking'].create({
            'partner_id': partner.id,
            'picking_type_id': picking_type.id,
            'location_id': location_src.id,
            'location_dest_id': location_dest.id,
            'origin': self.workorder_id.production_id.name,
            # 'company_id': self.workorder_id.company_id.id,
        })

        # Tạo dòng di chuyển sản phẩm
        self.env['stock.move'].create({
            'picking_id': new_picking.id,
            'product_id': self.raw_material.id,  # Sử dụng raw_material
            'product_uom_qty': self.quantity_by_material,  # Sử dụng quantity_by_material
            'product_uom': self.raw_material.uom_id.id,
            'name': self.raw_material.name,
            # 'company_id': self.workorder_id.company_id.id,
            'location_id': location_src.id,
            'location_dest_id': location_dest.id,
            'state': 'assigned',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công!',
                'message': f"Đã tạo phiếu bổ sung cho lệnh sản xuất {self.workorder_id.production_id.name}",
                'type': 'success',  # Loại thông báo: success, warning, danger
                'sticky': False,    # Thông báo tự động ẩn sau vài giây
            },
        }     