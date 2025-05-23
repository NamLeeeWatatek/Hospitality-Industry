from odoo import fields, models

# Kế thừa (mở rộng) model 'stock.move.line' có sẵn trong Odoo
class StockMoveLineReport(models.Model):
    _inherit = 'stock.move.line'

    # Trường 'product_default_code' để lấy mã sản phẩm từ product_id
    product_default_code = fields.Char(
        string="Mã sản phẩm", # Nhãn hiển thị trên giao diện
        related='product_id.default_code', # Liên kết với trường 'default_code' của model 'product.product'
        store=True, # Lưu vào database để có thể tìm kiếm và lọc dữ liệu
    )

    # Trường Boolean để xác định đơn hàng có phải là đơn hàng nhà hay không
    is_home_order = fields.Boolean(string="Is Home Order", default=True)

    # Trường Boolean để xác định đơn hàng có phải là đơn hàng ký gửi hay không
    is_consignment_order = fields.Boolean(string="Is Consignment Order", default=True)