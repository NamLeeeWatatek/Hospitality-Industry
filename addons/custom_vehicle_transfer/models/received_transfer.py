from odoo import models, fields, api

class ReceivedTransfer(models.Model):
    _name = 'received.transfer'
    _description = 'Received Transfer'

    order_line_id = fields.Many2one('sale.order.line', string='Order Line', ondelete='cascade')
    order_id = fields.Many2one(related='order_line_id.order_id')
    invoice_id = fields.Many2one('account.move', compute='_compute_invoice')

    date = fields.Datetime(string='Ngày/Tháng/Năm', related='order_id.date_order')
    invoice_number = fields.Char(string='Mã hóa đơn', related='invoice_id.name')
    customer = fields.Char(string='Khách hàng', related='order_id.partner_id.name')
    name = fields.Char(string='Tên hàng', related='order_line_id.product_id.name')
    province = fields.Char(string='Đơn vị tính', related='order_line_id.unit_of_measure')
    regulation = fields.Char(string='Quy cách', compute='_compute_regulation')
    quantity = fields.Float(string='Số lượng', related='order_line_id.billing_qty')
    unit_price = fields.Float(string='Đơn giá', related='order_line_id.price_unit')
    currency_id = fields.Many2one(related='order_id.currency_id')
    total_price = fields.Monetary(string='Thành tiền', related='order_line_id.price_subtotal', currency_field='currency_id')
    currency = fields.Char(string='Loại tiền', related='order_id.currency_id.name')
    payment_vn = fields.Char(string='Thu VN', compute='_compute_payment')
    payment_cpc = fields.Char(string='Thu CPC', compute='_compute_payment')
    status_in_payment = fields.Char(string='HTTT', compute='_compute_status_in_payment')
    invoice_date_due = fields.Date(string='Ngày thanh toán', related='invoice_id.invoice_date_due')
    

    @api.depends('order_id.invoice_ids.state')
    def _compute_invoice(self):
        for record in self:
            record.invoice_id = False
            if record.order_id:
                invoice = record.order_id.invoice_ids.filtered(lambda inv: inv.state == 'posted')
                if invoice:
                    record.invoice_id = invoice[:1]

    @api.depends('invoice_id.status_in_payment')
    def _compute_status_in_payment(self):
        for record in self:
            if record.invoice_id.status_in_payment == 'paid':
                record.status_in_payment = 'Đã thanh toán'
            elif record.invoice_id.status_in_payment == 'unpaid':
                record.status_in_payment = 'Chưa thanh toán'
            else:
                record.status_in_payment = 'Chưa thanh toán'

    @api.depends('order_id.consignment_fee_collector')
    def _compute_payment(self):
        for record in self:
            if record.order_id.consignment_fee_collector == 'hcm':
                record.payment_vn = 'Thu VN'
                record.payment_cpc = ''
            elif record.order_id.consignment_fee_collector == 'campuchia':
                record.payment_vn = ''
                record.payment_cpc = 'Thu CPC'
            else:
                record.payment_vn = ''
                record.payment_cpc = '' 

    @api.depends('order_line_id.consignment_packed_type', 'order_line_id.product_uom_qty')
    def _compute_regulation(self):
        for record in self:
            if record.order_line_id.consignment_packed_type and record.order_line_id.product_uom_qty:
                packed_type = record.order_line_id.consignment_packed_type
                quantity = int(record.order_line_id.product_uom_qty)
                record.regulation = f"loại {quantity} {packed_type}"
            else:
                record.regulation = ''