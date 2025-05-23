from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = "account.journal"

    def open_action(self):
        action = super(AccountJournal, self).open_action()
        print(">>> Hàm open_action() được gọi với journal: %s", self.code)

        if self.code == "HDKG":
            list_view_id = self.env.ref('custom_invoices.custom_invoice_consignment_list').id
            form_view_id = self.env.ref('consignment.consignment_invoice_form_view').id  # Đảm bảo view này tồn tại và là form view

            action['context'] = dict(
                action.get('context', {}),
                form_view_initial_mode='edit',
                view_mode='list,form'
            )
            action['views'] = [(list_view_id, 'list'), (form_view_id, 'form')]
            # Nếu cần search view:
            # action['search_view_id'] = self.env.ref('custom_invoices.custom_invoice_consignment_filter').id
            
            # Tìm các hóa đơn liên quan đến journal này và cập nhật is_consignment_invoice
            invoices = self.env['account.move'].search([('journal_id', '=', self.id)])
            if invoices:
                invoices.write({'is_consignment_invoice': True})
                print(">>> Đã cập nhật is_consignment_invoice thành True cho %s hóa đơn", len(invoices))

        return action
