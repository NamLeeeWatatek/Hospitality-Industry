from odoo import models, fields, api, _

class ConsignmentInvoice(models.Model):
    _inherit = 'account.move'

    is_consignment_invoice = fields.Boolean(string="Is Consignment Invoice", default=False)

    display_move_type = fields.Char(
        string="Loại hóa đơn", compute="_compute_display_move_type", store=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        invoices = super().create(vals_list)
        return invoices

    def action_post(self):
        target_company = self.env["res.company"].browse(2)

        for move in self:

            sale_order = self.env["sale.order"].search([("name", "=", move.invoice_origin)], limit=1)

            if self.is_consignment_invoice and sale_order.consignment_fee_collector == "campuchia":
                
                # Chuyển company_id trước cho move
                move.sudo().write({"company_id": target_company.id})

                # Gọi super trước để hệ thống tạo xong các dòng journal
                res = super().action_post()

                # Sau đó sửa lại tất cả account_id và company_id cho các dòng
                receivable_account = self.env["account.account"].with_company(target_company).search([
                    ("account_type", "=", "asset_receivable")
                ], limit=1)

                income_account = self.env["account.account"].with_company(target_company).search([
                    ("account_type", "=", "income")
                ], limit=1)

                # Lấy tất cả các dòng của hóa đơn và sửa lại account_id và company_id
                for line in move.line_ids:
                    updates = {}
                    if line.account_id.account_type == "income":
                        updates["account_id"] = income_account.id
                    elif line.account_id.account_type == "asset_receivable":
                        updates["account_id"] = receivable_account.id

                    if updates:
                        updates["company_id"] = target_company.id
                        updates["date_maturity"] = move.invoice_date_due or move.date or fields.Date.today()
                        line.with_context(tracking_disable=True).sudo().write(updates)

                return res

        # Trường hợp không phải consignment thì cứ gọi super bình thường
        return super().action_post()

    @api.depends("move_type", "is_consignment_invoice")
    def _compute_display_move_type(self):
        move_type_mapping = {
            "entry": _("Bút toán"),
            "out_invoice": _("Hóa đơn bán hàng"),
            "out_refund": _("Giấy báo có khách hàng"),
            "in_invoice": _("Hóa đơn mua hàng"),
            "in_refund": _("Giấy báo có nhà cung cấp"),
            "out_receipt": _("Biên lai bán hàng"),
            "in_receipt": _("Biên lai mua hàng"),
        }
        for record in self:
            if record.is_consignment_invoice:
                record.display_move_type = _("Hóa đơn ký gửi")
            else:
                record.display_move_type = move_type_mapping.get(record.move_type, record.move_type)

    def action_view_source_sale_orders(self):
        self.ensure_one()
        action = self.env.ref("sale.action_orders").read()[0]

        sale_orders = self.invoice_line_ids.mapped("sale_line_ids.order_id")
        if not sale_orders:
            return action

        action["res_id"] = sale_orders.id
        
        # Kiểm tra nếu là đơn hàng ký gửi thì chỉ hiển thị view ký gửi, không thêm trùng views
        if self.is_consignment_invoice:
            action["views"] = [(self.env.ref("consignment.view_sale_order_form_consignment").id, "form")]
        else:
            action["views"] = [(self.env.ref("sale.view_order_form").id, "form")]

        return action

