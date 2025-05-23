from odoo import models, fields

# Kế thừa (mở rộng) model 'stock.move.line' có sẵn trong Odoo
class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

 # Thêm trường mới 'picking_type_id'
    picking_type_id = fields.Many2one('stock.picking.type', string="Picking Type", related="picking_id.picking_type_id", store=True)


