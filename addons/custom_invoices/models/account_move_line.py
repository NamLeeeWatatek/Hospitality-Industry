from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    consignment_packed_type = fields.Char(string="Quy cách")
    unit_of_measure = fields.Char(string="ĐVT")

    