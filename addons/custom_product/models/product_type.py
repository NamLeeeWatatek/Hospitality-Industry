from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_type = fields.Selection([
        ('home_product', 'Hàng nhà'),
        ('consignment_product', 'Hàng kí gửi'),
    ], string="Loại hàng", required=True, default='home_product')

