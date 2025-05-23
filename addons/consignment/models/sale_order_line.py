from odoo import models, fields, api
from odoo.tools import float_compare, float_is_zero
import logging

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    received_qty = fields.Float(
        string='Số lượng nhận ký gửi',
        readonly=True,
        compute="_compute_received_qty",
        store=False,
    )

    consignment_delivered_qty = fields.Float(
        string='Số lượng đã giao ký gửi',
        readonly=True,
        compute="_compute_consignment_qty_delivered",
        store=False,
    )

    billing_qty = fields.Float(string="Số lượng", required=True, default=1.0)

    def _prepare_invoice_line(self, **optional_values):
        """Ghi đè để đưa consignment_packed_type và unit_of_measure vào invoice"""
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)

        if self.order_id.is_consignment_order:
            res.update({
                'quantity': self.billing_qty,
                'consignment_packed_type': f"{self.product_uom_qty} {self.consignment_packed_type}".strip() if self.consignment_packed_type else str(self.product_uom_qty),
            })
        
        res['unit_of_measure'] = self.unit_of_measure

        return res

    @api.depends('product_uom_qty', 'billing_qty', 'discount', 'price_unit', 'tax_id', 'order_id.is_consignment_order')
    def _compute_amount(self):
        """
        Tính toán lại `price_subtotal` dựa trên `billing_qty` nếu `is_consignment_order` là True.
        """
        for line in self:
            qty = line.billing_qty if line.order_id.is_consignment_order else line.product_uom_qty
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.depends('order_id.name')
    def _compute_received_qty(self):
        for line in self:
            if not line.order_id or not line.order_id.is_consignment_order:
                line.received_qty = 0
                continue
            
            pickings = self.env['stock.picking'].search([
                ('origin', '=', line.order_id.name),
                ('picking_type_id.code', '=', 'incoming'),
                ('state', '=', 'done')
            ])

            if not line.order_id.is_consignment_order:
                line.received_qty = 0
                continue
            
            total_received = 0
            for picking in pickings:
                moves = picking.move_ids.filtered(lambda m: 
                    m.product_id.id == line.product_id.id and
                    m.consignment_packed_type == line.consignment_packed_type and
                    m.unit_of_measure == line.unit_of_measure
                )

                total_received += sum(m.quantity for m in moves)

            line.received_qty = total_received

    @api.depends('order_id.name')
    def _compute_consignment_qty_delivered(self):
        consignment_lines = self.filtered(lambda l: l.order_id and l.order_id.is_consignment_order)
        for line in consignment_lines:
            pickings = self.env['stock.picking'].search([
                ('origin', '=', line.order_id.name),
                ('picking_type_id.code', '=', 'outgoing'),
                ('state', '=', 'done')
            ])

            total_delivered = 0
            for picking in pickings:
                moves = picking.move_ids.filtered(lambda m:
                    m.product_id.id == line.product_id.id and
                    m.consignment_packed_type == line.consignment_packed_type and
                    m.unit_of_measure == line.unit_of_measure
                )
                total_delivered += sum(m.quantity for m in moves)

            line.consignment_delivered_qty = total_delivered
            
        for line in self:
            if line.order_id.is_consignment_order:
                line.order_id._check_consignment_received()

    @api.depends_context('lang')
    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id')
    def _compute_tax_totals(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)

            base_lines = []
            for line in order_lines:
                base_line = line._prepare_base_line_for_taxes_computation()

                # Nếu là hàng ký gửi, dùng billing_qty thay vì product_uom_qty
                if order.is_consignment_order:
                    base_line['quantity'] = line.billing_qty
                else:
                    base_line['quantity'] = line.product_uom_qty

                base_lines.append(base_line)

            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)

            order.tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'state', 'order_id.is_consignment_order')
    def _compute_qty_to_invoice(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.state == 'sale' and not line.display_type:
                qty_ordered = line.billing_qty if line.order_id.is_consignment_order else line.product_uom_qty

                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = qty_ordered - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice', 'qty_invoiced', 'order_id.is_consignment_order')
    def _compute_invoice_status(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            qty_ordered = line.billing_qty if line.order_id.is_consignment_order else line.product_uom_qty

            if line.state != 'sale':
                line.invoice_status = 'no'
            elif line.is_downpayment and line.untaxed_amount_to_invoice == 0:
                line.invoice_status = 'invoiced'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and qty_ordered >= 0.0 and \
                    float_compare(line.qty_delivered, qty_ordered, precision_digits=precision) == 1:
                line.invoice_status = 'upselling'
            elif float_compare(line.qty_invoiced, qty_ordered, precision_digits=precision) == 0 or \
                float_compare(line.qty_invoiced, qty_ordered, precision_digits=precision) == 1:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no'