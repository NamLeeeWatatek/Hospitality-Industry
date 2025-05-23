from odoo import models, fields, api

class Vehicle(models.Model):
    _name = 'vehicle.management'
    _description = 'Quản lý xe'
    _rec_name = 'license_plate'  # Dùng license_plate thay cho name
    name = fields.Char(string='Mã số xe', required=True, copy=False, readonly=True, default='New')
    license_plate = fields.Char(string='Biển số xe', required=True)
    state = fields.Selection([
        ('active', 'Hoạt động'),
        ('inactive', 'Không hoạt động'),
        ('maintenance', 'Bảo trì'),
    ], string='Trạng thái', default='active')
    description = fields.Text(string='Mô tả')
    status_history_ids = fields.One2many('vehicle.status.history', 'vehicle_id', string='Lịch sử trạng thái')
    active = fields.Boolean(string='Hoạt động', default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.management') or 'New'
        return super(Vehicle, self).create(vals_list)

    def action_unarchive(self):
        self.write({'active': True})