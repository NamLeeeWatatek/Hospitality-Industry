from odoo import models, fields, api

class VehicleTransferDateFilterWizard(models.TransientModel):
    _name = 'vehicle.transfer.date.filter.wizard'
    _description = 'Wizard to Filter Vehicle Transfer by Date'

    date_filter = fields.Date(string='Ngày lọc', required=True, default=fields.Date.today)

    def action_apply_filter(self):
        self.ensure_one()
        # Tạo domain để lọc các bản ghi có date_utc khớp với ngày được chọn
        domain = [('date_utc', '=', self.date_filter)]
        # Trả về action để cập nhật domain trên list view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vehicle.transfer',
            'view_mode': 'list',
            'domain': domain,
            'target': 'current',
            'name': 'Hàng hóa đã chuyển',
        }