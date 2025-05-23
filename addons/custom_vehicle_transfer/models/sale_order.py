from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vehicle_transfer_ids = fields.One2many(
        'vehicle.transfer', 'order_id', string='Vehicle Transfers',
    )
    received_transfer_ids = fields.One2many(
        'received.transfer', 'order_id', string='Received Transfers',
    )
    deliveried_transfer_ids = fields.One2many(
        'deliveried.transfer', 'order_id', string='Deliveried Transfers',
    )

    def _prepare_vehicle_transfer(self):
        self.ensure_one()
        order_line = self.order_line
        vals_list = []
        for line in order_line:
            vals = {
                'order_line_id': line.id,
            }
            vals_list.append(vals)
        return vals_list
    
    def _prepare_received_transfer(self):
        order_line = self.order_line
        vals_list = []
        for line in order_line:
            vals = {
                'order_line_id': line.id,
            }
            vals_list.append(vals)
        return vals_list

    def _prepare_deliveried_transfer(self):
        order_line = self.order_line
        vals_list = []
        for line in order_line:
            vals = {
                'order_line_id': line.id,
            }
            vals_list.append(vals)
        return vals_list

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if res:
            for order in self:
                # if order.is_consignment_order and order.state == 'sale' and not order.vehicle_transfer_ids:
                #     # Create vehicle transfer
                #     vals_list = order._prepare_vehicle_transfer()
                #     self.env['vehicle.transfer'].create(vals_list)
                if order.is_consignment_order and order.state == 'sale' and not order.received_transfer_ids:
                    # Create received transfer
                    vals_list = order._prepare_received_transfer()
                    self.env['received.transfer'].create(vals_list)
                if not order.is_consignment_order and order.state == 'sale' and not order.deliveried_transfer_ids:
                    # Create deliveried transfer
                    vals_list = order._prepare_deliveried_transfer()
                    self.env['deliveried.transfer'].create(vals_list)
        return res