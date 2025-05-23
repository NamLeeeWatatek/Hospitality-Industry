from odoo import models

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def button_open_invoices(self):
        action = super(AccountPayment, self).button_open_invoices()

        self.ensure_one()
        move = self.reconciled_invoice_ids[:1]
        if move and move.is_consignment_invoice:
            view_id = self.env.ref('consignment.consignment_invoice_form_view').id
            action['views'] = [(view_id, 'form')]
            action['view_id'] = view_id

        return action