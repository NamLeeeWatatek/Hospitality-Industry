from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    vehicle_transfer_ids = fields.One2many(
        'vehicle.transfer', 'invoice_id', string='Vehicle Transfers',
    )
    received_transfer_ids = fields.One2many(
        'received.transfer', 'invoice_id', string='Received Transfers',
    )
    deliveried_transfer_ids = fields.One2many(
        'deliveried.transfer', 'invoice_id', string='Deliveried Transfers',
    )

    def _prepare_vehicle_transfer(self, move):
        order_line = self.line_ids.sale_line_ids
        vals_list = []
        for line in order_line:
            vals = {
                'order_line_id': line.id,
                'invoice_id': move.id,
            }
            vals_list.append(vals)
        return vals_list
    
    def _prepare_received_transfer(self, move):
        order_line = self.line_ids.sale_line_ids
        vals_list = []
        for line in order_line:
            vals = {
                'order_line_id': line.id,
                'invoice_id': move.id,
            }
            vals_list.append(vals)
        return vals_list

    def _prepare_deliveried_transfer(self, move):
        order_line = self.line_ids.sale_line_ids
        vals_list = []
        for line in order_line:
            vals = {
                'order_line_id': line.id,
                'invoice_id': move.id,
            }
            vals_list.append(vals)
        return vals_list

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for move in self:
            if move.is_consignment_invoice and move.state == 'posted' and 'state' in vals and not move.vehicle_transfer_ids:
                # Create vehicle transfer
                vals_list = self._prepare_vehicle_transfer(move)
                self.env['vehicle.transfer'].create(vals_list)
            if move.is_consignment_invoice and move.state == 'posted' and 'state' in vals and not move.received_transfer_ids:
                # Create received transfer
                vals_list = self._prepare_received_transfer(move)
                self.env['received.transfer'].create(vals_list)
            if not move.is_consignment_invoice and move.state == 'posted' and 'state' in vals and not move.deliveried_transfer_ids:
                # Create deliveried transfer
                vals_list = self._prepare_deliveried_transfer(move)
                self.env['deliveried.transfer'].create(vals_list)
        return res