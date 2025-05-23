from odoo import models, fields, api

class VehicleStatusWizard(models.TransientModel):
    _name = 'vehicle.status.wizard'
    _description = 'Thay đổi trạng thái xe'

    vehicle_id = fields.Many2one('vehicle.management', string='Xe', required=True)
    status = fields.Selection([
        ('active', 'Hoạt động'),
        ('inactive', 'Không hoạt động'),
        ('maintenance', 'Bảo trì'),
    ], string='Trạng thái mới', required=True)

    def action_confirm(self):
        for wizard in self:
            wizard.vehicle_id.write({'state': wizard.status})
        return {'type': 'ir.actions.act_window_close'}