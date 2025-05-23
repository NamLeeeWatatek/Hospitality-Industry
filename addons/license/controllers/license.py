from odoo import http
from odoo.http import request
import json
from datetime import datetime, timedelta
import logging

class LicenseController(http.Controller):

    def expiration(self):
        # Tính toán ngày hết hạn mới
        new_expiration_date = (datetime.now() + timedelta(days=365*100)).strftime('%Y-%m-%d %H:%M:%S')

        # Cập nhật các tham số cấu hình
        ICP = request.env['ir.config_parameter'].sudo()
        ICP.set_param('database.expiration_date', new_expiration_date)
        ICP.set_param('database.license', '100Years')
        ICP.set_param('database.create_date', datetime.now())
        ICP.set_param('database.expiration_reason', False)

        logging.info(f"License:|__________New expiration date: {new_expiration_date}__________|")
        
        return new_expiration_date  # Return the new expiration date

    @http.route('/license', auth='user', type='http', csrf=False)
    def session(self):

        if not request.env.user.has_group('base.group_system'):
            return request.not_found("You are not authorized to access this page")  # Hoặc trả về lỗi 403

        self.expiration()
        session_info = request.env['ir.http'].session_info()

        return request.make_response(
            json.dumps({
                "session_info": session_info,
            }),
            headers=[('Content-Type', 'application/json')] 
        )