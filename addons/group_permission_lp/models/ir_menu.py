from odoo import models, api

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def get_user_roots(self):
        menus = super().get_user_roots()

        user = self.env.user
        company_ids = user.company_ids.ids 

        # Nếu user không thuộc công ty có ID 3 thì ẩn menu Sale
        if 3 not in company_ids:
            sale_menu = self.env.ref('sale.sale_menu_root', raise_if_not_found=False)
            if sale_menu:
                menus = menus.filtered(lambda menu: menu.id != sale_menu.id)

        # Nếu user không thuộc công ty có ID 1 thì ẩn menu Purchase
        if 1 not in company_ids:
            purchase_menu = self.env.ref('purchase.menu_purchase_root', raise_if_not_found=False)
            if purchase_menu:
                menus = menus.filtered(lambda menu: menu.id != purchase_menu.id)

        # Nếu user không có cả công ty 1 và 2 thì ẩn menu Consignment
        if not (1 in company_ids or 2 in company_ids):  # Chỉ ẩn nếu cả 1 và 2 đều không có
            consignment_menu = self.env.ref('consignment.quan_ly_ky_gui', raise_if_not_found=False)
            if consignment_menu:
                menus = menus.filtered(lambda menu: menu.id != consignment_menu.id)
        
        return menus