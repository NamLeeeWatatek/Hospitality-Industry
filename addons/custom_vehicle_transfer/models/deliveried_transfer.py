from odoo import models, fields, api

class DeliveriedTransfer(models.Model):
    _name = 'deliveried.transfer'
    _description = 'Deliveried Transfer'

    order_line_id = fields.Many2one('sale.order.line', string='Order Line', ondelete='cascade')
    order_id = fields.Many2one(related='order_line_id.order_id')
    invoice_id = fields.Many2one('account.move', compute='_compute_invoice')

    date = fields.Datetime(string='Ngày giao hàng', compute='_compute_picking')
    delivery_employee = fields.Char(string='Người giao hàng', compute='_compute_picking')
    customer = fields.Char(string='Khách hàng', related='order_id.partner_id.name')
    name = fields.Char(string='Loại hàng', related='order_line_id.product_id.name')
    province = fields.Char(string='ĐVT', related='order_line_id.unit_of_measure')
    quantity = fields.Float(string='SL', related='order_line_id.billing_qty')
    unit_price = fields.Float(string='Đơn giá', related='order_line_id.price_unit')
    currency_id = fields.Many2one(related='order_id.currency_id')
    total_price = fields.Monetary(string='Thành tiền', related='order_line_id.price_subtotal', currency_field='currency_id')
    actual_currency_id = fields.Many2one(related='invoice_id.actual_currency_id')
    received_aba = fields.Monetary(string='ABA', compute='_compute_payment', currency_field='actual_currency_id')
    received_cash = fields.Monetary(string='Tiền mặt', compute='_compute_payment', currency_field='actual_currency_id')
    debit_cash = fields.Monetary(string='Tiền mặt', compute='_compute_payment', currency_field='currency_id')
    payment_date = fields.Date(string='Ngày trả', compute='_compute_payment')

    @api.depends('order_id.invoice_ids.state')
    def _compute_invoice(self):
        for record in self:
            record.invoice_id = False
            if record.order_id:
                invoice = record.order_id.invoice_ids.filtered(lambda inv: inv.state == 'posted')
                if invoice:
                    record.invoice_id = invoice[:1]

    @api.depends('order_line_id')
    def _compute_picking(self):
        for record in self:
            if record.order_line_id:
                pickings = record.order_line_id.move_ids.picking_id
                record.date = pickings[:1].scheduled_date
                record.delivery_employee = pickings[:1].ten_tai_xe
            else:
                record.date = ''
                record.delivery_employee = ''
    
    @api.depends('invoice_id.payment_ids.state')
    def _compute_payment(self):
        for record in self:
            record.received_aba = 0.0
            record.received_cash = 0.0
            record.debit_cash = 0.0
            record.payment_date = ''
            if record.invoice_id:
                payment = record.invoice_id.matched_payment_ids.filtered(lambda p: p.state == 'paid')
                if payment.journal_id.type == 'bank':
                    record.received_aba = payment.actual_amount_paid
                else:
                    record.received_cash = payment.actual_amount_paid
                record.debit_cash = payment.amount - payment.actual_amount_paid
                record.payment_date = record.invoice_id.invoice_date_due