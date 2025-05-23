from odoo import models, fields, api
from odoo.tools import formatLang

class AccountMove(models.Model):
    _inherit = "account.move"

    actual_amount_paid = fields.Monetary(
        string="Số tiền thực tế trả",
        currency_field="actual_currency_id",
        compute="_compute_actual_amount_paid",
    )
    actual_currency_id = fields.Many2one(
        'res.currency', string="Loại tiền thực tế",
        compute='_compute_actual_amount_paid'
    )

    @api.depends('payment_ids', 'actual_amount_paid')
    def _compute_actual_amount_paid(self):
        for record in self:
            payments = record.payment_ids.filtered(lambda p: p.actual_amount_paid > 0)
            record.actual_amount_paid = sum(payment.actual_amount_paid for payment in payments)
            record.actual_currency_id = payments and payments[0].actual_currency_id or False
            
    def _compute_payments_widget_reconciled_info(self):
        super()._compute_payments_widget_reconciled_info()
        for move in self:
            if move.invoice_payments_widget:
                if move.state == 'posted' and move.is_invoice(include_receipts=True):
                    reconciled_partials = move._get_all_reconciled_invoice_partials()
                    for i, reconciled_partial in enumerate(reconciled_partials):
                        counterpart_line = reconciled_partial['aml']
                        move.invoice_payments_widget['content'][i].update({
                            'actual_amount_paid': formatLang(self.env, abs(counterpart_line.move_id.actual_amount_paid), currency_obj=counterpart_line.move_id.actual_currency_id),
                        })
