from odoo import models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        param = self.env['ir.config_parameter'].sudo().get_param('default_home_discuss.default_home_action_id')
        if param:
            for vals in vals_list:
                if not vals.get('action_id'):
                    vals['action_id'] = int(param)
        return super().create(vals_list)