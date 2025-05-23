from odoo import models, fields, api

class PurchaseWarningWizard(models.TransientModel):
    _name = 'purchase.warning.wizard'
    _description = 'Purchase Order Warning'

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")

    def confirm_order(self):
        if self.purchase_order_id:
            self.purchase_order_id.is_confirmed = True
            self.purchase_order_id.button_confirm()
        return {'type': 'ir.actions.act_window_close'}