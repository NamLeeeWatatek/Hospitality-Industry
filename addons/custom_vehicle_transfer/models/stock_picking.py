from odoo import models
from collections import defaultdict

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()

        if res is True:
            vals_list = []

            for picking in self.filtered(lambda p: p.is_transit_out):
                if picking.company_id.id != 1:
                    continue

                for move in picking.move_ids:
                    serials = move.lot_ids.mapped('name')

                    in_lines = self.env['stock.move.line'].search([
                        ('lot_id.name', 'in', serials),
                        ('state', '=', 'done'),
                        ('product_id', '=', move.product_id.id),
                        ('move_id.picking_code', '=', 'incoming'),
                    ])

                    if not in_lines:
                        continue

                    # Group lines by picking_id and sum qty
                    picking_qty_map = defaultdict(float)
                    for line in in_lines:
                        picking_qty_map[line.move_id.picking_id] += line.quantity

                    for picking_in, total_qty in picking_qty_map.items():
                        origins = picking_in.origin and [picking_in.origin] or []

                        so_list = self.env['sale.order'].search([('name', 'in', origins)])

                        for so in so_list:
                            if not so.is_consignment_order:
                                continue
                            so_lines = so.order_line.filtered(lambda x: x.product_id == move.product_id)
                            invoice = so.invoice_ids.filtered(lambda x: x.state == 'posted')
                            for so_line in so_lines:
                                vals_list.append({
                                    'order_line_id': so_line.id,
                                    'invoice_id': invoice.id,
                                    'transit_picking_id': picking.id,
                                    'consignment_transfer': True,
                                    'quantity': total_qty,
                                })

            if vals_list:
                self.env['vehicle.transfer'].create(vals_list)

        return res