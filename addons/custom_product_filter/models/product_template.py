from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_category_type_display = fields.Char(
        string="Loại hàng hóa",
        compute="_compute_product_category_type_display",
        store=False,
    )

    def _compute_product_category_type_display(self):
        for record in self:
            if record.type == 'product':
                record.product_category_type_display = 'Hàng nhà'
            elif record.type == 'consu':
                record.product_category_type_display = 'Hàng ký gửi'
            else:
                record.product_category_type_display = 'Khác'