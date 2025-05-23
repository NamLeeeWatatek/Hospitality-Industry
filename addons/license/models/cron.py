from odoo import models, api
import datetime

class IrCronUpdate(models.AbstractModel):
    _name = 'ir.cron.update'
    _description = 'Update license every time odoo start'

    def _register_hook(self):
        """Chạy mỗi lần Odoo khởi động"""
        super()._register_hook()
        self.run_license_expiration()

    @api.model
    def run_license_expiration(self):
        """Gọi expiration() của model license"""
        self.env['license'].sudo().expiration()