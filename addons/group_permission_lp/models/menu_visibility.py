from odoo import models, api

class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    @api.model
    def get_user_roots(self):

        res = super().get_user_roots()
        
        return res