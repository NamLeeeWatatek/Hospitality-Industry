
from odoo import models, fields , api

class ConsignmentPicking(models.Model):
    _inherit = 'stock.picking'

    is_consignment = fields.Boolean(string="Is Consignment", default=False)
    def action_open_label_type(self):
        view = self.env.ref('stock.picking_label_type_form')
        lot_ids = self.move_ids_without_package.mapped('lot_ids').ids
        move_lines_with_lot = self.move_ids_without_package.mapped('move_line_ids').filtered(lambda l: l.lot_id)

        return {
            'name': _('Chọn loại nhãn in'),
            'type': 'ir.actions.act_window',
            'res_model': 'picking.label.type',
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': {'default_picking_ids': self.ids,
            'default_lot_ids': lot_ids,
            'default_move_line_ids': [(6, 0, move_lines_with_lot.ids)],},
        }

    def action_view_consignment_order(self):

        """Mở Sale Order từ phiếu nhập kho ký gửi với view tùy chỉnh"""
        self.ensure_one()

        
        if self.is_consignment and self.origin:
            sale_order = self.env["sale.order"].search(
                [("name", "=", self.origin)], limit=1
            )

            if sale_order:
                return {
                    "name": "Đơn Ký Gửi",
                    "view_mode": "form",
                    "res_model": "sale.order",
                    "type": "ir.actions.act_window",
                    "res_id": sale_order.id,
                    "view_id": self.env.ref(
                        "consignment.view_sale_order_form_consignment"
                    ).id,
                }

        return {"type": "ir.actions.act_window_close"}


    # @api.model
    # def get_action_click_graph(self):
    #     """Ghi đè phương thức để trả về action tùy chỉnh."""
    #     action = self.env.ref("stock.action_picking_tree_graph", raise_if_not_found=False)
    #     if action:
    #         # Đọc dữ liệu action
    #         action_data = action.read()[0]

    #         # In thông tin kiểm tra trước khi cập nhật (màu vàng)
    #         print("\033[93mAction Data Before Update:\033[0m", action_data)

    #         # Cập nhật context để đảm bảo sử dụng action tùy chỉnh
    #         action_data.update({
    #             'context': {
    #                 'contact_display': 'partner_address',
    #                 'search_default_available': 1,
    #                 'search_default_waiting': 1,
    #                 'form_view_ref': 'consignment.stock_picking_form_view',
    #                 'default_is_consignment': True,
    #             }
    #         })

    #         # In thông tin sau khi cập nhật (màu xanh lá)
    #         print("\033[92mAction Data After Update:\033[0m", action_data)

    #         return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Cần làm',
    #             'res_model': 'stock.picking',
    #             'view_mode': 'list,kanban,form,calendar',
    #             'context': {
    #                 'contact_display': 'partner_address',
    #                 'search_default_available': 1,
    #                 'search_default_waiting': 1,
    #                 'form_view_ref': 'consignment.stock_picking_form_view',
    #                 'default_is_consignment': True,
    #             },
    #         }
    #     else:
    #         # In thông báo lỗi (màu đỏ)
    #         print("\033[91mAction 'stock.action_picking_tree_graph' không tìm thấy.\033[0m")
    #         return {}

    # @api.model
    # def get_action_click_graph(self):
    #     """Gọi action 'action_picking_tree_graph'."""

    #     action = self.env.ref("consignment.action_picking_tree_graph", raise_if_not_found=False)
    #     if action:
    #         # Trả về action đã được định nghĩa trong XML
    #         return action.read()[0]
    #     else:
    #         # Nếu action không tồn tại, trả về thông báo lỗi
    #         return {"type": "ir.actions.act_window_close"}




    # @api.model
    # def get_action_click_graph(self):
    #     """Gọi action 'action_picking_tree_graph' với điều kiện picking_type_id = 9 hoặc 10."""

    #     action_consignment = self.env.ref("consignment.action_picking_tree_graph", raise_if_not_found=False)

    #     action_consignment_data = action_consignment.read()[0]


    #         # Kiểm tra điều kiện picking_type_id
    #     if self.env["stock.picking"].search([("picking_type_id", "in", [9, 10])]):
    #             # Trả về action đã được định nghĩa trong XML
    #             return action_consignment_data
    #     else:
    #             # Nếu không thỏa mãn điều kiện, trả về thông báo lỗi
    #             return {"type": "ir.actions.act_window_close"}


    
    
    @api.model
    def get_action_click_graph(self):
        action_consignment = self.env.ref("consignment.action_picking_tree_graph", raise_if_not_found=False)

        action_consignment_data = action_consignment.read()[0]

        action = self.env.ref("stock.action_picking_tree_graph", raise_if_not_found=False)

        action_data = action.read()[0]

        # Lấy picking_type_id từ context một cách an toàn
        picking_type_id = self.env.context.get('default_picking_type_id') or self.env.context.get('search_default_picking_type_id') or False

        print(">>> Context:", self.env.context)
        print(">>> Picking Type ID từ context:", picking_type_id)

        if picking_type_id:
            # Xử lý trường hợp picking_type_id là danh sách
            if isinstance(picking_type_id, (list, tuple)):
                picking_type_id = picking_type_id[0] if picking_type_id else False

            print(">>> Picking Type ID sau khi xử lý:", picking_type_id)

            # Đảm bảo ID hợp lệ trước khi truy vấn
            try:
                picking_type = self.env['stock.picking.type'].browse(picking_type_id)
                if picking_type.exists():  # Kiểm tra xem bản ghi có tồn tại không
                    print(">>> Người dùng đang lọc theo Loại Phiếu:", picking_type.name)
                    # Kiểm tra giá trị picking_type_id
                    if picking_type_id in (9,10,17,18):
                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'Cần làm',
                            'res_model': 'stock.picking',
                            'view_mode': 'list,kanban,form,calendar',
                            'context': {
                                'contact_display': 'partner_address',
                                'search_default_available': 1,
                                'search_default_waiting': 1,
                                'form_view_ref': 'consignment.stock_picking_form_view',
                                'default_is_consignment': True,
                            }
                        }
                    elif picking_type_id in (1, 2,25,26):
                        return action_data
                    else:
                        # Trường hợp mặc định nếu picking_type_id không phải 1, 2, hoặc 9
                        print(">>> Picking Type ID không khớp với điều kiện, trả về action mặc định.", picking_type_id)
                        return action_data
                else:
                    print(">>> Picking Type ID không tồn tại trong cơ sở dữ liệu.")
                    return action_data  # Trả về mặc định nếu bản ghi không tồn tại
            except Exception as e:
                print(">>> Lỗi khi lấy thông tin Loại Phiếu:", str(e))
                return action_data  # Trả về mặc định nếu có lỗi
        else:
            print(">>> Không có Loại Phiếu nào được chọn trong tìm kiếm.")
            return action_data  # Trả về mặc định nếu không có picking_type_id

    def action_assign(self):
        res = super().action_assign()

        for picking in self:
            if not picking.is_consignment or not picking.partner_id:
                continue

            for move in picking.move_ids_without_package:
                for move_line in move.move_line_ids:
                    quants = self.env['stock.quant'].sudo().search([
                        ('product_id', '=', move.product_id.id),
                        ('owner_id', '=', picking.partner_id.id),
                        ('quantity', '>', 0),
                        ('reserved_quantity', '=', 0),
                        ('location_id', '=', move_line.location_id.id),
                    ], order='quantity desc')

                    matched = False
                    for quant in quants:
                        if quant.quantity >= move_line.quantity:
                            move_line.sudo().write({
                                'quant_id': quant.id,
                                'unit_of_measure': move.unit_of_measure,
                            })
                            matched = True
                            break

                    if not matched:
                        move_line.sudo().unlink()

        return res
