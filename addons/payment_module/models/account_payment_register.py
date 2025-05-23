from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    actual_amount_paid = fields.Monetary(
        string="Số tiền thực tế trả",
        currency_field="actual_currency_id"
    )
    actual_currency_id = fields.Many2one(
            'res.currency',
            string="Tiền tệ",
            default=lambda self: self.env.company.currency_id.id,
            required=True
        )   
    invoice_id = fields.Many2one('account.move', string="Hóa đơn cần thanh toán")
    partner_phone = fields.Char(string="Số điện thoại", compute="_compute_partner_info")
    partner_address = fields.Char(string="Địa chỉ", compute="_compute_partner_info")

    @api.depends("partner_id")
    def _compute_partner_info(self):
        for record in self:
            if record.partner_id:
                record.partner_phone = record.partner_id.phone or ''
                record.partner_address = record.partner_id.contact_address or ''
    def _create_payments(self):
        payments = super()._create_payments()
        for payment in payments:
            payment.invoice_id = self.invoice_id
            payment.actual_amount_paid = self.actual_amount_paid
            payment.actual_currency_id = self.actual_currency_id
        return payments

    def create_payment(self):
        """Tạo payment và đảm bảo liên kết đúng với hóa đơn"""
        _logger.info("Bắt đầu tạo payment...")

        payment_vals = {
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'actual_amount_paid': self.actual_amount_paid,
            'actual_currency_id': self.actual_currency_id.id,
            'invoice_id': self.invoice_id.id if self.invoice_id else False,
        }

        payment = self.env['account.payment'].create(payment_vals)

        if self.invoice_id:
            self.invoice_id.actual_amount_paid = (self.invoice_id.actual_amount_paid or 0) + self.actual_amount_paid
            self.invoice_id.actual_currency_id = self.actual_currency_id.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'res_id': payment.id,
            'view_mode': 'form',
            'target': 'current',
        }