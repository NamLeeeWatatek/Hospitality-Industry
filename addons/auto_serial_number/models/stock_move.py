from odoo import models, _, api
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model_create_multi
    def create(self, vals_list):
        """ 
        Ghi đè logic để cập nhật số lượng và đơn vị tính cho stock.move từ purchase.order.line.
        Nếu có ít nhất một move thuộc backorder, thì bỏ qua logic update từ purchase_line. 
        """
        for vals in vals_list:
            purchase_line_id = vals.get('purchase_line_id')

            if purchase_line_id:
                purchase_line = self.env['purchase.order.line'].browse(purchase_line_id)
                if purchase_line:
                    if any(
                        v.get('product_uom') == purchase_line.product_uom.id 
                        and v.get('product_uom_qty', 0) < purchase_line.product_qty
                        for v in vals_list
                    ):
                        return super(StockMove, self).create(vals_list)
        for vals in vals_list:
            purchase_line_id = vals.get('purchase_line_id') 

            if purchase_line_id:
                purchase_line = self.env['purchase.order.line'].browse(purchase_line_id)
                if purchase_line:
                    vals.update({
                        'product_uom': purchase_line.product_uom.id,
                        'product_uom_qty': purchase_line.product_qty,
                    })
                    if purchase_line.dvt:
                        vals['unit_of_measure'] = purchase_line.dvt

        return super(StockMove, self).create(vals_list)

    def _action_confirm(self, merge=False, merge_into=False):
        res = super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)

        for move in self:

            if move.company_id.id != 1:  
                continue

            if move.picking_type_id.code != 'incoming' or move.product_id.tracking not in ['lot', 'serial']:
                continue

            if move.purchase_line_id and move.product_uom_qty == 0:
                move.product_uom_qty = move.purchase_line_id.product_qty
                move.product_uom = move.purchase_line_id.product_uom

            if (move.product_uom_qty < 1 or move.product_uom_qty % 1 != 0) and move.product_id.tracking == 'serial':
                raise UserError("Số lượng sản phẩm nhận ký gửi được theo dõi theo Seri, không được là số lẻ.")

            if (move.product_uom_qty < 1 or move.product_uom_qty % 1 != 0) and move.product_id.tracking == 'lot' and move.product_id.product_type == 'consignment_product':
                raise UserError("Số lượng sản phẩm nhận ký gửi được theo dõi theo Seri, không được là số lẻ.")

            if (move.product_uom_qty % 1 != 0) and move.product_id.tracking == 'lot':
                raise UserError("Số lượng sản phẩm hàng nhà không được là số lẻ. Vui lòng nhập số lượng nguyên. Nếu muốn nhập lẻ, vui lòng đổi quy cách sản phẩm. (VD: 1,5 10KG -> 3 5KG)")

            if int(move.product_uom_qty) >= 1:
                move._create_move_lines()

        return res

    def _create_move_lines(self):
        StockMoveLine = self.env['stock.move.line']
        StockLot = self.env['stock.lot']

        for move in self:
            if move.product_id.tracking not in ['lot', 'serial']:
                continue

            new_lines = []
            original_lines = move.move_line_ids.filtered(lambda ml: ml.product_id == move.product_id)

            lot_dict = {}  # Lưu trữ các lot đã được tạo để tránh việc tạo lại lot nhiều lần

            for ml in original_lines:
                qty = int(ml.quantity or 0)
                if qty <= 1:
                    ml.qty_done = 1.0
                    new_lines.append(ml)
                    continue

                vals = {
                    'move_id': move.id,
                    'product_id': move.product_id.id,
                    'location_id': ml.location_id.id,
                    'location_dest_id': ml.location_dest_id.id,
                    'picking_id': move.picking_id.id,
                    'company_id': move.company_id.id,
                    'owner_id': move.picking_id.owner_id.id,
                    'product_uom_id': move.product_uom.id,
                    'unit_of_measure': move.unit_of_measure,
                    'consignment_packed_type': move.consignment_packed_type,
                }

                ml.unlink()  # Xóa dòng hiện tại

                for _ in range(qty):
                    new_line = StockMoveLine.create({
                        **vals,
                        'quantity': 1.0,
                        'qty_done': 1.0,
                    })
                    new_lines.append(new_line)

            # Tính lại padding để có số lượng cho lot_name
            padding = len(str(len(new_lines)))

            filtered_moves = move.picking_id.move_ids.filtered(
                lambda m: m.product_id == move.product_id and m.picking_id == move.picking_id
            )
            move_index = next(
                (i + 1 for i, m in enumerate(sorted(filtered_moves, key=lambda m: m.id)) if m == move),
                1
            )

            picking_name = move.picking_id.name or ''
            parts = picking_name.split("/")
            short_name = parts[0][:2] + "/" + parts[-1] if len(parts) >= 2 else picking_name

            # Tạo hoặc gán lot_name vào move.line
            for i, ml in enumerate(sorted(new_lines, key=lambda m: m.id), 1):
                lot_name = f"{short_name}-{move_index}-{str(i).zfill(padding)}"

                # Kiểm tra xem lot đã tồn tại trong dict chưa
                if lot_name not in lot_dict:
                    lot = StockLot.search([
                        ('name', '=', lot_name),
                        ('product_id', '=', move.product_id.id)
                    ], limit=1)

                    if not lot:
                        lot = StockLot.create({
                            'name': lot_name,
                            'product_id': move.product_id.id,
                            'company_id': move.company_id.id,
                        })

                    lot_dict[lot_name] = lot

                ml.lot_id = lot_dict[lot_name]
                ml.write({'lot_name': lot_name})  # Gắn lot_name vào dòng di chuyển
