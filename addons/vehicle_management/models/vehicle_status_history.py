# vehicle_management/models/vehicle_status_history.py
from odoo import models, fields

class VehicleStatusHistory(models.Model):
    _name = 'vehicle.status.history'
    _description = 'Lịch sử trạng thái xe'

    vehicle_id = fields.Many2one('vehicle.management', string='Xe')
    status = fields.Selection([
        ('active', 'Hoạt động'),
        ('inactive', 'Không hoạt động'),
        ('maintenance', 'Bảo trì'),
    ], string='Trạng thái')
    change_date = fields.Date(string='Ngày thay đổi')