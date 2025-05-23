from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_own_stock = fields.Boolean(
        string="Hàng nhà",
        compute="_compute_stock_ownership",
        store=True,
        help="Sản phẩm có product_type là Hàng nhà."
    )
    is_consignment_stock = fields.Boolean(
        string="Hàng ký gửi",
        compute="_compute_stock_ownership",
        store=True,
        help="Sản phẩm có product_type là Hàng ký gửi."
    )

    @api.depends('product_tmpl_id.product_type')
    def _compute_stock_ownership(self):
        for product in self:
            # Lấy product_type từ product.template
            product_type = product.product_tmpl_id.product_type

            # Log để debug
            _logger.info("Product %s: product_type = %s", product.name, product_type)

            # Kiểm tra Hàng nhà
            product.is_own_stock = product_type == 'home_product'

            # Kiểm tra Hàng ký gửi
            product.is_consignment_stock = product_type == 'consignment_product'

            # Log kết quả
            _logger.info("Product %s: is_own_stock = %s, is_consignment_stock = %s",
                         product.name, product.is_own_stock, product.is_consignment_stock)
            
    @api.model
    def get_current_warehouses(self):
        warehouses = self.search([])
        return [{
            'id': warehouse.id,
            'name': warehouse.name,
            'is_consignment': warehouse.is_consignment,
        } for warehouse in warehouses]