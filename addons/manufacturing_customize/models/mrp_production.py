from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    don_ban_hang = fields.Many2one('sale.order', string='Đơn bán hàng')
    ti_le_ng = fields.Float(string='Tỉ lệ NG', compute='_compute_ti_le_ng', store=True)
    
    @api.depends('qty_producing', 'product_qty')
    def _compute_ti_le_ng(self):
        for record in self:
            if record.qty_producing != 0:
                record.ti_le_ng = ((record.product_qty - record.qty_producing) / record.product_qty)
            else:
                record.ti_le_ng = 0

    def create_picking_and_moves(self, picking_type_name, production):
        picking_type = self.env['stock.picking.type'].search([('name', '=', picking_type_name)], limit=1)
        if not picking_type:
            raise UserError(f"Không tìm thấy loại phiếu '{picking_type_name}'")

        location_src = picking_type.default_location_src_id
        location_dest = picking_type.default_location_dest_id
        partner = self.env.user.partner_id

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': location_src.id,
            'location_dest_id': location_dest.id,
            'partner_id': partner.id,
            'origin': production.name,
            'don_ban_hang': production.don_ban_hang.id,
            'bom_of_product': production.bom_id.id,
        })

        stock_move = self.env['stock.move'].create({
            'picking_id': picking.id,
            'product_id': production.product_id.id,
            'product_uom_qty': production.qty_produced,
            'product_uom': production.product_uom_id.id,
            'name': production.product_id.name,
            'company_id': picking.company_id.id,
            'location_id': location_src.id,
            'location_dest_id': location_dest.id,
            'state': 'draft',
        })

        if production.lot_producing_id:
            self.env['stock.move.line'].create({
                'move_id': stock_move.id,
                'product_id': production.product_id.id,
                'product_uom_id': production.product_uom_id.id,
                'qty_done': production.qty_produced,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'lot_id': production.lot_producing_id.id,
                'picking_id': picking.id,
            })
        else:
            self.env['stock.move.line'].create({
                'move_id': stock_move.id,
                'product_id': production.product_id.id,
                'product_uom_id': production.product_uom_id.id,
                'qty_done': production.qty_produced,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'lot_id': False,
                'picking_id': picking.id,
            })

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()

        if self.state == 'done':  # Kiểm tra trạng thái của bản ghi
            if self.name.startswith('KSX'):
                # Chuyển qua kho QC
                self.create_picking_and_moves('Lệnh chuyển hàng nội bộ KSX', self)
                # Xác định dạng bom
                bom_type = self.env['mrp.bom'].search([('id', '=', self.bom_id.id)], limit=1)
                # Bom dạng cuộn
                if bom_type.quy_cach_dong_goi == "Cuộn":
                    self.bom_cuon(self.qty_producing, self)
                if bom_type.quy_cach_dong_goi == "Tờ":
                    # Tạo phiếu đóng gói
                    self.create_picking_and_moves('Đóng gói', self)
                    # Chuyển về kho thành phẩm
                    self.create_picking_and_moves('Lệnh chuyển hàng nội bộ KQC', self)
                    # Tạo phiếu nhập kho ở kho thành phẩm
                    self.create_picking_and_moves('Phiếu nhập kho KTP', self)
                    # Đánh dấu là đã xử lý
                    # self.is_processed = True

            if self.name.startswith('KQC'):
                # Tạo phiếu đóng gói
                self.create_picking_and_moves('Đóng gói', self)
                # Chuyển về kho thành phẩm
                self.create_picking_and_moves('Lệnh chuyển hàng nội bộ KQC', self)
                # Tạo phiếu nhập kho ở kho thành phẩm
                self.create_picking_and_moves('Phiếu nhập kho KTP', self)

        return res

    def bom_cuon(self, qty_producing, production_production):
        picking_type = self.env['stock.picking.type'].search([('name', '=', 'Đóng gói bằng máy')], limit=1)
        if not picking_type:
            raise UserError("Không tìm thấy loại phiếu 'Đóng gói bằng máy'")

        product = self.product_tmpl_id.product_variant_id
        bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.product_tmpl_id.id)], limit=1)

        production = self.env['mrp.production'].create({
            'picking_type_id': picking_type.id,
            'product_id': product.id,
            'product_qty': qty_producing,
            'bom_id': production_production.bom_id.id,
            'location_src_id': picking_type.default_location_src_id.id,
            'location_dest_id': picking_type.default_location_dest_id.id,
            'don_ban_hang': production_production.don_ban_hang.id,
        })

        stock_move = self.env['stock.move'].create({
            'product_id': product.id,
            'product_uom_qty': qty_producing,
            'product_uom': product.uom_id.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': production.location_src_id.id,
            'raw_material_production_id': production.id,
            'company_id': self.env.company.id,
            'state': 'draft',
        })

        raw_moves = production.move_raw_ids.filtered(lambda move: move.product_id != product)
        raw_moves.unlink()

        workorders = production.workorder_ids
        workorders.unlink()
    
    @api.onchange('product_id', 'move_raw_ids', 'never_product_template_attribute_value_ids')
    def _onchange_product_id(self):
        return

    def request_materials_button(self):
        env = self.env
        # Tìm loại phiếu
        picking_type_name = 'Phiếu giao nguyên liệu'
        picking_type = env['stock.picking.type'].search([('name', '=', picking_type_name)], limit=1)
        if not picking_type:
            raise UserError(f"Không tìm thấy loại phiếu '{picking_type_name}'")

        location_src = picking_type.default_location_src_id
        location_dest = picking_type.default_location_dest_id
        partner = env.user.partner_id

        # Tạo phiếu vận chuyển mới
        new_picking = env['stock.picking'].create({
            'partner_id': partner.id,
            'picking_type_id': picking_type.id,
            'location_id': location_src.id,
            'location_dest_id': location_dest.id,
            'origin': self.name,
            'company_id': self.company_id.id,
            'don_ban_hang': self.don_ban_hang.id if self.don_ban_hang else False,
            'bom_of_product': self.bom_id.id if self.bom_id else False,
            'state': 'assigned',
        })

        # Lặp qua các nguyên liệu trong move_raw_ids (nguyên liệu cần dùng)
        for move in self.move_raw_ids:
            if move.product_uom_qty <= 0:
                raise UserError(f"Số lượng nguyên liệu '{move.product_id.name}' không hợp lệ.")

            # Tạo dòng move cho nguyên liệu
            new_move = env['stock.move'].create({
                'picking_id': new_picking.id,
                'product_id': move.product_id.id,
                'product_uom_qty': move.product_uom_qty,  # Số lượng cần dùng
                'product_uom': move.product_uom.id,
                'name': move.product_id.name,
                'company_id': self.company_id.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'state': 'assigned',
            })

            # Tạo move line cho từng nguyên liệu
            env['stock.move.line'].create({
                'move_id': new_move.id,
                'product_id': move.product_id.id,
                'product_uom_id': move.product_uom.id,
                # 'qty_done': move.product_uom_qty,  # Số lượng thực tế cần dùng
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'lot_id': move.lot_ids.id if move.lot_ids else False,
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Thành công!',
                'message': f"Đã tạo phiếu nhận nguyên liệu cho đơn sản xuất {self.name}.",
                'type': 'success',
                'sticky': False,
            },
        }