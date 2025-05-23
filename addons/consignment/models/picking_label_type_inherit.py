# -*- coding: utf-8 -*-
from odoo import _, fields, models, api

class ProductLabelLayoutInherit(models.TransientModel):
    _inherit = 'picking.label.type'

    move_line_ids = fields.Many2many('stock.move.line')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move_line_ids = self.env.context.get('default_move_line_ids', [])
        res['move_line_ids'] = move_line_ids
        return res

    def process(self):
        if not self.picking_ids:
            return
        if self.label_type == 'products':
            return self.picking_ids.action_open_label_layout()

        view = self.env.ref('stock.lot_label_layout_form_picking')
        return {
            'name': _('Chọn bố cục nhãn in'),
            'type': 'ir.actions.act_window',
            'res_model': 'lot.label.layout',
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': {'default_move_line_ids': self.move_line_ids.ids},
        }