from odoo import models, api


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def get_stock_picking_action_picking_type(self):
        """Chọn action phù hợp dựa vào địa điểm đích"""

        consignment_action = self._get_action(
            "consignment.stock_picking_action_picking_type"
        )
        default_action = self._get_action("stock.stock_picking_action_picking_type")
        consignment_action_delivery = self._get_action(
            "custom_sale.stock_picking_action_picking_type_delivery"
        )
        consignment_action_receipt = self._get_action(
            "custom_sale.stock_picking_action_picking_type_receipt"
        )

        pickings_count = self.env["stock.picking"].search_count(
            [
                ("picking_type_id", "in", self.ids),
                "|",  # Toán tử OR
                ("location_dest_id.complete_name", "ilike", "KG%"),
                ("location_id.complete_name", "ilike", "KG%"),
            ]
        )
        # Kiểm tra nếu ID 17 có trong danh sách self.ids, trả về hành động nhập kho
        if 17 in self.ids:
            return consignment_action_receipt
        # Nếu ID 18 có trong danh sách self.ids, trả về hành động xuất kho
        if 18 in self.ids:
            return consignment_action_delivery

        if pickings_count:
            return consignment_action

        return default_action

    def get_action_picking_tree_ready(self):
        """Chọn action phù hợp dựa vào địa điểm đích"""

        pickings_count = self.env["stock.picking"].search_count(
            [
                ("picking_type_id", "in", self.ids),
                "|",  # Toán tử OR
                ("location_dest_id.complete_name", "ilike", "KG%"),
                ("location_id.complete_name", "ilike", "KG%"),
            ]
        )
        if pickings_count:
            return self._get_action("consignment.consignment_action_picking_tree_ready")
        else:
            home_product_action = self._get_action(
                "consignment.action_picking_tree_ready"
            )
            return home_product_action

