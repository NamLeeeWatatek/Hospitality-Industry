from odoo import models, fields, api
from datetime import date

class AccountMove(models.Model):
    _inherit = 'account.move'

    alert = fields.Boolean(string="Công nợ quá hạn", compute="_compute_alert", store=True)
    overdue_partner = fields.Char(string="Khách hàng nợ", compute="_compute_overdue_partner", store=True)

    @api.depends('invoice_date_due', 'payment_state')
    def _compute_alert(self):
        """Xác định hóa đơn có bị quá hạn hay không"""
        for record in self:
            record.alert = record.invoice_date_due and record.invoice_date_due < date.today() and record.payment_state != 'paid'

    @api.depends('alert', 'partner_id')
    def _compute_overdue_partner(self):
        """Gán tên khách hàng vào trường overdue_partner nếu hóa đơn bị quá hạn"""
        for record in self:
            record.overdue_partner = record.partner_id.name if record.alert else ""

    def action_send_due_alert(self):
        """Gửi thông báo khi hóa đơn quá hạn"""
        for invoice in self:
            if invoice.alert:
                message = f"Hóa đơn {invoice.name} của khách hàng {invoice.partner_id.name} đã quá hạn thanh toán!"
                self.env['bus.notification'].create({
                    'channel': 'mail.channel',
                    'message': message,
                    'user_id': invoice.invoice_user_id.id  # Gửi cho user phụ trách hóa đơn
                })
