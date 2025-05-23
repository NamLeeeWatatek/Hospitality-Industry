from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.onchange('product_id')
    def _onchange_product_id_show_lot(self):
        """ Khi chọn sản phẩm mới, nếu có tracking, thì hiện trường lot_id """
        if self.product_id.tracking != 'none':
            self.lot_id = self.env['stock.lot'].search([('product_id', '=', self.product_id.id)], limit=1)
