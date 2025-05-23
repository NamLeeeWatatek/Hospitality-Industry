from odoo import models, api, fields, _


class MailMessage(models.Model):
    _inherit = 'mail.message'

    is_hide_price = fields.Boolean(compute='_compute_is_hide_price', store=True)
    is_hide_price_po = fields.Boolean(compute='_compute_is_hide_price', store=True)
    
    @api.depends('model', 'subtype_id', 'tracking_value_ids')
    def _compute_is_hide_price(self):
        for r in self:
            r.is_hide_price = False
            r.is_hide_price_po = False
            if r.model == 'sale.order' and r.subtype_id and r.subtype_id.id == 2:
                tracking_value = r.tracking_value_ids.filtered(lambda x: x.field_id.id in (6588, 6586))
                if tracking_value:
                    r.is_hide_price = True
            elif r.model == 'purchase.order' and r.subtype_id and r.subtype_id.id == 2:
                tracking_value = r.tracking_value_ids.filtered(lambda x: x.field_id.id == 11600)
                if tracking_value:
                    r.is_hide_price_po = True
         
    @api.model           
    def update_hide_mail_message(self):
        messages = self.search(['|', ('model', '=', 'sale.order'), ('model', '=', 'purchase.order'), ('subtype_id', '=', 2)])
        messages._compute_is_hide_price()