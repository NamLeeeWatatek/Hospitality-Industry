from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = "account.journal"

    def open_action(self):
        action = super(AccountJournal, self).open_action()
        if self.code == "HDKG":
            view_id = self.env.ref('consignment.consignment_invoice_form_view').id
            action['context'] = dict(action.get('context', {}), form_view_initial_mode='edit', view_mode='list,form')
            action['views'] = [(False, 'list'), (view_id, 'form')]
        return action

    def action_create_new(self):
        action = super(AccountJournal, self).action_create_new()
        if self.code == "HDKG":
            view_id = self.env.ref('consignment.consignment_invoice_form_view').id
            action['views'] = [(view_id, 'form')]
            action['view_id'] = view_id
        return action