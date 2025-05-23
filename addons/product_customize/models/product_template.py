from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    standare_c1 = fields.Float(
        string='Chi phí sản xuất dự kiến',
        help='Chi phí sản xuất dự kiến của sản phẩm.'
    )