from odoo import models, api, fields
from datetime import datetime

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_confirm(self):
        """Ghi đè action_confirm để tự động tạo phiếu nhập kho từ HCM sang Campuchia."""
        # Gọi hàm gốc để thực hiện logic xác nhận mặc định
        result = super(StockPicking, self).action_confirm()

        # Chỉ xử lý nếu là phiếu xuất kho từ HCM
        for picking in self:
            if picking.picking_type_id.code == 'outgoing' and picking.location_id.name == 'HCM':
                # Tạo phiếu nhập kho tại Campuchia
                picking._create_import_picking()

        return result

    def _create_import_picking(self):
        """Tạo phiếu nhập kho từ HCM sang Campuchia."""
        StockPicking = self.env['stock.picking']

        # Tìm kho Campuchia (kho đích)
        campuchia_location = self.env['stock.location'].search([
            ('name', '=', 'Campuchia'),
            ('usage', '=', 'internal')
        ], limit=1)
        if not campuchia_location:
            raise ValueError("Không tìm thấy địa điểm 'Campuchia' trong hệ thống.")

        # Tìm kho HCM (kho nguồn)
        hcm_location = self.env['stock.location'].search([
            ('name', '=', 'HCM'),
            ('usage', '=', 'internal')
        ], limit=1)
        if not hcm_location:
            raise ValueError("Không tìm thấy địa điểm 'HCM' trong hệ thống.")

        # Tìm warehouse liên quan đến kho Campuchia
        warehouse = self.env['stock.warehouse'].search([
            ('view_location_id', 'parent_of', campuchia_location.id)
        ], limit=1)
        if not warehouse:
            raise ValueError(f"Không tìm thấy kho ứng với địa điểm '{campuchia_location.name}'.")

        # Tìm picking type cho nhập kho tại Campuchia
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id', '=', warehouse.id),
            ('default_location_dest_id', '=', campuchia_location.id)
        ], limit=1)
        if not picking_type:
            # Nếu không tìm thấy picking type phù hợp, tạo mới hoặc tìm picking type mặc định
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'incoming'),
                ('warehouse_id', '=', warehouse.id)
            ], limit=1)
            if not picking_type:
                raise ValueError(f"Không tìm thấy quy trình nhập kho cho {warehouse.name}")

        # Tạo phiếu nhập kho
        picking_vals = {
            'partner_id': self.partner_id.id if self.partner_id else False,
            'origin': self.name,
            'picking_type_id': picking_type.id,
            'location_id': hcm_location.id,  # Kho nguồn: HCM
            'location_dest_id': campuchia_location.id,  # Kho đích: Campuchia
            'scheduled_date': fields.Datetime.now(),  # Ngày kế hoạch
            'move_ids_without_package': []
        }

        # Thêm danh sách sản phẩm từ phiếu xuất kho
        for move in self.move_ids_without_package:
            picking_vals['move_ids_without_package'].append((0, 0, {
                'name': move.product_id.name,
                'product_id': move.product_id.id,
                'product_uom_qty': move.product_uom_qty,
                'product_uom': move.product_uom.id,
                'location_id': hcm_location.id,
                'location_dest_id': campuchia_location.id,
            }))

        # Tạo phiếu nhập kho
        new_picking = StockPicking.create(picking_vals)
        new_picking.action_confirm()
        new_picking.action_assign()

        return new_picking