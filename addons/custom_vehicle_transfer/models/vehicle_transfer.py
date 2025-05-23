from odoo import models, fields, api

class VehicleTransfer(models.Model):
    _name = 'vehicle.transfer'
    _description = 'Vehicle Transfer'

    order_line_id = fields.Many2one('sale.order.line', string='Order Line', ondelete='cascade')
    order_id = fields.Many2one(string='Đơn ký gửi',related='order_line_id.order_id')
    invoice_id = fields.Many2one('account.move', compute='_compute_invoice')
    transit_picking_id = fields.Many2one('stock.picking', string='Picking')
    date = fields.Datetime(string='Ngày/Tháng/Năm', related='transit_picking_id.date_done')
    date_utc = fields.Date(string='Ngày', compute='_compute_date_utc', store=True)
    vehicle_number = fields.Char(string='Số xe', compute='_compute_vehicle_number', store=True)
    contract_number = fields.Char(string='Mã hóa đơn', related='invoice_id.name')
    customer = fields.Char(string='Khách hàng', compute='_compute_partner_name', store=True)
    name = fields.Char(string='Tên hàng', related='order_line_id.product_id.name')
    province = fields.Char(string='Đơn vị tính', related='order_line_id.unit_of_measure')
    regulation = fields.Char(string='Quy cách', related='order_line_id.consignment_packed_type')
    quantity = fields.Float(string='SL đóng gói đã chuyển')
    move_qty = fields.Float(string='SL đóng gói', related='order_line_id.product_uom_qty')
    invoice_qty = fields.Float(string='Số lượng', related='order_line_id.billing_qty')
    unit_price = fields.Float(string='Đơn giá', related='order_line_id.price_unit')
    currency_id = fields.Many2one(related='order_id.currency_id')
    total_price = fields.Monetary(string='Thành tiền', related='order_line_id.price_subtotal', currency_field='currency_id')
    currency = fields.Char(string='Loại tiền', related='order_id.currency_id.name')
    payment_vn = fields.Char(string='Thu VN', compute='_compute_payment')
    payment_cpc = fields.Char(string='Thu CPC', compute='_compute_payment')
    consignment_transfer = fields.Boolean(string="Hàng ký gửi", default=False)
    
    @api.depends('date')
    def _compute_date_utc(self):
        for record in self:
            if record.date:
                # Chuyển date sang múi giờ người dùng (+7)
                user_tz = record.env.user.tz or 'Asia/Ho_Chi_Minh'
                date_in_user_tz = fields.Datetime.context_timestamp(record.with_context(tz=user_tz), record.date)
                record.date_utc = date_in_user_tz.date()
            else:
                record.date_utc = False

    @api.depends('order_id.partner_id.name')
    def _compute_partner_name(self):
        for record in self:
            record.customer = record.order_id.partner_id.name + " - " + record.order_id.partner_id.phone
    
    @api.depends('order_id.invoice_ids.state')
    def _compute_invoice(self):
        for record in self:
            record.invoice_id = False
            if record.order_id:
                invoice = record.order_id.invoice_ids.filtered(lambda inv: inv.state == 'posted')
                if invoice:
                    record.invoice_id = invoice[:1]
    
    @api.depends('order_line_id')
    def _compute_vehicle_number(self):
        for record in self:
            if record.transit_picking_id:
                record.vehicle_number = record.transit_picking_id.bien_so_xe
            else:
                record.vehicle_number = ''
    
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
            if record.consignment_transfer:
                record.regulation = record.order_line_id.consignment_packed_type
            else:
                record.regulation = record.order_line_id.product_uom_qty


    def action_open_custom_sale_order(self):
        self.ensure_one()
        if not self.order_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đơn hàng ký gửi',
            'res_model': 'sale.order',
            'res_id': self.order_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('consignment.view_sale_order_form_consignment').id,
            'target': 'current',
        }