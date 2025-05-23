from odoo import models
from odoo.http import request
from datetime import datetime, timedelta
import logging

class LicenseModel(models.Model):
    _name = 'license'
    _description = 'License Controller'

    def expiration(self):
        # Tính toán ngày hết hạn mới
        new_expiration_date = (datetime.now() + timedelta(days=365*100)).strftime('%Y-%m-%d %H:%M:%S')

        # Cập nhật các tham số cấu hình
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('database.create_date', datetime.now())
        ICP.set_param('database.expiration_date', new_expiration_date)
        ICP.set_param('database.license', '100Years')
        ICP.set_param('database.expiration_reason', False)

        logging.info(f"License:🚀 New expiration date: {new_expiration_date} 🔥🔥🔥")
        
        return new_expiration_date  # Return the new expiration date