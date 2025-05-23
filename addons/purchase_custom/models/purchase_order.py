from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_confirmed = fields.Boolean(default=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['picking_type_id'] = 1
        return super().create(vals_list)

    def button_confirm(self):
        for order in self:
            if not order.is_confirmed and any(line.product_qty > 1000 for line in order.order_line):
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Cảnh báo'),
                    'res_model': 'purchase.warning.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_purchase_order_id': order.id},
                }
        return super(PurchaseOrder, self).button_confirm()

    def action_send_order(self):  
        """Chuyển đơn hàng từ 'draft' sang 'sent'"""  
        for order in self: 
            order.write({"state": "sent"})  
