from odoo import models, fields

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    def _get_advance_payment_method_selection(self):
        # Lấy danh sách selection gốc từ model cha
        parent_model = super(SaleAdvancePaymentInv, self)
        # Kiểm tra xem trường 'advance_payment_method' có tồn tại không
        if 'advance_payment_method' not in parent_model._fields:
            # Nếu không tồn tại, trả về danh sách mặc định chỉ có 'delivered'
            return [('delivered', 'Hóa đơn thường xuyên')]

        selection = parent_model._fields['advance_payment_method'].selection
        if callable(selection):
            # Nếu selection là một hàm, gọi hàm đó để lấy danh sách
            selection = selection(self)

        # Đảm bảo selection là một iterable, nếu không thì trả về danh sách mặc định
        if not isinstance(selection, (list, tuple)):
            return [('delivered', 'Hóa đơn thường xuyên')]

        # Chỉ giữ lại tùy chọn 'delivered' (Hóa đơn thường xuyên)
        filtered_selection = [(key, value) for key, value in selection if key == 'delivered']

        # Đảm bảo có ít nhất một giá trị mặc định
        if not filtered_selection:
            filtered_selection = [('delivered', 'Hóa đơn thường xuyên')]

        return filtered_selection

    # Ghi đè trường advance_payment_method
    advance_payment_method = fields.Selection(
        selection='_get_advance_payment_method_selection',
        string='What do you want to invoice?',
        default='delivered',
        required=True,
    )
    def create_invoices(self):
        self.ensure_one()

        sale_orders = self.env["sale.order"].browse(self._context.get("active_ids", []))

        # Nếu là đơn ký gửi, dùng sudo để tránh lỗi công ty
        is_consignment = all(so.is_consignment_order for so in sale_orders)

        if is_consignment:
            sale_orders = sale_orders.sudo()
            # Override active_ids in context for super
            ctx = dict(self.env.context, active_ids=sale_orders.ids)
            invoices = super(SaleAdvancePaymentInv, self.with_context(ctx).sudo()).create_invoices()
        else:
            invoices = super(SaleAdvancePaymentInv, self).create_invoices()

        if isinstance(invoices, dict) and invoices.get("res_model") == "account.move":
            invoices = self.env["account.move"].browse(invoices.get("res_id"))
        elif not isinstance(invoices, models.Model):
            if isinstance(invoices, list) and all(isinstance(i, int) for i in invoices):
                invoices = self.env["account.move"].browse(invoices)
            elif isinstance(invoices, (int, str)):
                invoices = self.env["account.move"].browse(int(invoices))
            else:
                return invoices

        for invoice in invoices.sudo():
            sale_orders_linked = invoice.invoice_line_ids.mapped("sale_line_ids.order_id")
            for so in sale_orders_linked:
                if so.is_consignment_order:
                    update_vals = {"is_consignment_invoice": True}
                    if so.consignment_fee_collector == "campuchia":
                        journal = self.env["account.journal"].search([
                            ("company_id", "=", 2), 
                            ("type", "=", "sale")
                        ], limit=1)
                        update_vals.update({
                            "company_id": 2,
                            "journal_id": journal.id,
                        })
                    else:
                        update_vals.update({"company_id": so.company_id.id})
                    invoice.sudo().write(update_vals)

        return invoices

