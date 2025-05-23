from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    consignment_packed_type = fields.Char(
        string="Quy cách", compute="_compute_packed_type", store=True
    )

    unit_of_measure = fields.Char(
        string="ĐVT", compute="_compute_unit_of_measure", store=True
    )

    packed_status = fields.Selection(
        [
            ("hcm_warehouse", "Đã nhập kho HCM"),
            ("in_transit", "Đang vận chuyển"),
            ("cam_warehouse", "Đã nhập kho CAM"),
            ("delivered", "Đã giao"),
        ],
        string="Trạng thái kiện hàng",
        compute="_compute_packed_status",  # Liên kết với phương thức tính toán
        store=True,  # Lưu giá trị vào cơ sở dữ liệu
        default="hcm_warehouse",
    )

    @api.depends("lot_id", "product_id", "location_id")
    def _compute_packed_type(self):
        for quant in self:
            move_lines = self.env["stock.move.line"].search(
                [
                    ("product_id", "=", quant.product_id.id),
                    ("lot_id", "=", quant.lot_id.id if quant.lot_id else False),
                    ("move_id.state", "=", "done"),
                    ("location_dest_id", "=", quant.location_id.id),
                ],
                order="date desc",
                limit=1,
            )

            quant.consignment_packed_type = (
                move_lines.move_id.consignment_packed_type if move_lines else ""
            )

    @api.depends("lot_id", "product_id", "location_id")
    def _compute_unit_of_measure(self):
        for quant in self:
            move_lines = self.env["stock.move.line"].search(
                [
                    ("product_id", "=", quant.product_id.id),
                    ("lot_id", "=", quant.lot_id.id if quant.lot_id else False),
                    ("move_id.state", "=", "done"),
                    ("location_dest_id", "=", quant.location_id.id),
                ],
                order="date desc",
                limit=1,
            )

            quant.unit_of_measure = (
                move_lines.move_id.unit_of_measure if move_lines else ""
            )

    @api.depends("location_id")
    def _compute_packed_status(self):
        """Đặt trạng thái in_transit nếu quant đang ở 'Địa điểm ảo/Xe vận chuyển'"""
        transit_location = self.env["stock.location"].search(
            [("complete_name", "=", "Địa điểm ảo/Xe vận chuyển")], limit=1
        )
        for quant in self:
            if quant.location_id == transit_location:
                quant.packed_status = "in_transit"
            else:
                quant.packed_status = "hcm_warehouse"

    def action_recompute_fields(self):
        quants = self.search([])
        quants._compute_packed_type()
        quants._compute_unit_of_measure()

    def open_transit_popup(self):
        action = self.env.ref("serialized_packages.action_open_transit_popup").read()[0]
        return action


# @api.depends("location_id", "product_id")
# def update_packed_status(self):
#     for quant in self:
#         move_lines = self.env["stock.move.line"].search(
#             [
#                 ("location_dest_id", "=", quant.location_id.id),
#                 ("product_id", "=", quant.product_id.id),
#                 ("state", "=", "done"),
#             ],
#             limit=1,
#         )

#         if move_lines:
#             quant.packed_status = "hcm_warehouse"  Chỉ cập nhật khi có dữ liệu hợp lệ
