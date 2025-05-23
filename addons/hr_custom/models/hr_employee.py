from odoo import models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.constrains('barcode')
    def _verify_barcode(self):
        # Ghi đè hàm thành rỗng
        return