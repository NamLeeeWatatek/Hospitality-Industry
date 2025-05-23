from odoo import models, fields

class StocktMoveLine(models.Model):
    _inherit = 'stock.move.line'

    consignment_packed_type = fields.Char(string="Quy cách")
    unit_of_measure = fields.Char(string="ĐVT")

    