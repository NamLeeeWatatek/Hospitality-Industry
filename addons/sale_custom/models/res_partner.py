from odoo import models, api
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []

        # Tìm theo x_ma_khachhang trước
        domain_x_ma_khachhang = expression.AND([[('x_ma_khachhang', operator, name)], args])
        records = self.search(domain_x_ma_khachhang, limit=limit)

        # Nếu không tìm thấy, tìm theo display_name mặc định
        if not records:
            domain_default = expression.AND([[('display_name', operator, name)], args])
            records = self.search(domain_default, limit=limit)

        return [(record.id, record.display_name) for record in records.sudo()]