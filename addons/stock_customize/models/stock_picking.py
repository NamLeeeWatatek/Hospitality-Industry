from odoo import models, fields
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    don_ban_hang = fields.Many2one('sale.order', string='Đơn bán hàng')
    bom_of_product = fields.Many2one(
        'mrp.bom', 
        string='BOM sản phẩm', 
        readonly=True
    )

    def create_picking_and_moves(self, picking_type_name, production):
        env = self.sudo().env
        # Tìm loại phiếu
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
            'origin': production.origin,
            'company_id': production.company_id.id,
            'don_ban_hang': getattr(production, 'don_ban_hang', False) and production.don_ban_hang.id or False,
            'bom_of_product': getattr(production, 'bom_of_product', False) and production.bom_of_product.id or False,
            'state': 'assigned',
        })

        # Lặp qua các dòng move của phiếu gốc
        for move in production.move_ids:
            if move.product_uom_qty <= 0:
                raise UserError(f"Số lượng sản phẩm '{move.product_id.name}' không hợp lệ.")

            new_move = env['stock.move'].create({
                'picking_id': new_picking.id,
                'product_id': move.product_id.id,
                'product_uom_qty': move.product_uom_qty,
                'product_uom': move.product_uom.id,
                'name': move.product_id.name,
                'company_id': production.company_id.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'state': 'assigned',
            })

            # # Xử lý từng lô nếu có
            # for lot in move.lot_ids:
            #     # Kiểm tra xem lot_id đã tồn tại trong stock.move.line hay chưa
            #     existing_move_line = env['stock.move.line'].search([
            #         ('move_id', '=', new_move.id),
            #         ('lot_id', '=', lot.id)
            #     ], limit=1)

            #     if existing_move_line:
            #         # Nếu đã tồn tại, bỏ qua hoặc cập nhật nếu cần
            #         continue

            #     # Tạo dòng move line mới nếu chưa tồn tại
            #     env['stock.move.line'].create({
            #         'move_id': new_move.id,
            #         'product_id': move.product_id.id,
            #         'product_uom_id': move.product_uom.id,
            #         'qty_done': 0,  # Số lượng thực tế ban đầu là 0
            #         'location_id': location_src.id,
            #         'location_dest_id': location_dest.id,
            #         'lot_id': lot.id,
            #     })

        return new_picking


    def button_validate(self):
            res = super(StockPicking, self).button_validate()

            if self.state == "done":  # Kiểm tra trạng thái của bản ghi
                # Chuyển qua phiếu nhận hàng
                if self.name.startswith("KNL/GNLOUT"):
                    self.create_picking_and_moves("Phiếu nhận nguyên liệu", self)
                if self.name.startswith("KRD/GK"):
                    self.create_picking_and_moves("Phiếu nhận khuôn", self)

            return res