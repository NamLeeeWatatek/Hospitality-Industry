from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order.line'
    
    production_cost = fields.Float(string="Chi phí sản xuất", copy=True)
    subcontracting_cost = fields.Float(string="Chi phí gia công", copy=True)
    other_cost = fields.Float(string="Chi phí khác", copy=True)

    @api.depends('production_cost', 'subcontracting_cost', 'other_cost')
    def _compute_margin(self):
        for line in self:
            # Tổng chi phí
            total_cost = (line.production_cost + line.subcontracting_cost + line.other_cost) * line.product_uom_qty
            # Lợi nhuận
            line.margin = line.price_subtotal - total_cost
            # Phần trăm lợi nhuận
            line.margin_percent = line.price_subtotal and (line.margin / line.price_subtotal) * 100
