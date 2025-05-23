from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    all_products_info = fields.Text(
        string="Sản phẩm & Số lượng",
        compute="_compute_all_products_info",
        store=True
    )

    @api.depends('invoice_line_ids')
    def _compute_all_products_info(self):
        for move in self:
            products = []
            for line in move.invoice_line_ids:
                product_info = f"- {line.product_id.name}: {line.quantity} {line.product_uom_id.name} | Đơn giá: {line.price_unit} {line.currency_id.name}"
                products.append(product_info)
            move.all_products_info = "\n".join(products) if products else "Không có sản phẩm"
