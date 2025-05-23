from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    actual_amount_paid = fields.Monetary(string="Số tiền thực tế trả", currency_field="actual_currency_id")
    actual_currency_id = fields.Many2one('res.currency', string="Loại tiền thực tế")
    partner_bank_id = fields.Many2one('res.partner.bank')
    show_partner_bank_account = fields.Boolean(default=False)    
    invoice_id = fields.Many2one(
                'account.move',
                string="Hóa đơn cần thanh toán",
                domain="[('move_type','=','out_invoice'),('payment_state','!=','paid')]"
            )

    def action_post(self):
        res = super().action_post()
        for payment in self:
            if payment.invoice_id:
                invoice = payment.invoice_id

                # Cập nhật số tiền thực tế đã thanh toán vào hóa đơn
                invoice.actual_amount_paid += payment.actual_amount_paid
                invoice.actual_currency_id = payment.actual_currency_id

                # Cập nhật trạng thái thanh toán nếu cần
                if invoice.amount_residual == 0:
                    invoice.payment_state = 'paid'

                invoice._compute_payment_state()
        return res

    def _get_payment_info(self):
        self.ensure_one()
        return {
            'content': self.payment_lines.mapped(lambda r: {
                'id': r.id,
                'amount': r.amount,
                'date': r.date,
                'journal_name': r.journal_id.name,
                'currency_id': r.currency_id.id,
            }),
            'move_id': self.move_id.id,
            'actual_amount_paid': self.actual_amount_paid or 0,
            'actual_currency_id': self.actual_currency_id.id,
        }