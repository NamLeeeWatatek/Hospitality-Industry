from odoo import models, fields

class StockLot(models.Model):
    _inherit = 'stock.lot'

    tuoi_dao = fields.Integer(
        string='Tuổi dao',
        help='Tuổi dao của lô/seri này.'
    )