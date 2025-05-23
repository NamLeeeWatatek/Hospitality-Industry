from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_home_action_id = fields.Many2one(
        'ir.actions.actions',
        string="Default Home Action",
        config_parameter='default_home_discuss.default_home_action_id',
        default=lambda self: self.env.ref('mail.action_discuss').id,
        default_model= 'ir.actions.actions',
    )

    def set_values(self):
        if self.default_home_action_id:
            action_id = self.default_home_action_id.id
            self.env['ir.config_parameter'].sudo().set_param(
                'default_home_discuss.default_home_action_id',
                str(action_id) 
            )

            self.env['res.users'].sudo().search([]).write({
                'action_id': action_id
            })
        super().set_values()

    @api.model
    def get_values(self):
        res = super().get_values()
        param_model = self.env['ir.config_parameter'].sudo()
        action_id = param_model.get_param('default_home_discuss.default_home_action_id')

        if not action_id:
            action = self.env.ref('mail.action_discuss', raise_if_not_found=False)
            if action:
                param_model.set_param('default_home_discuss.default_home_action_id', str(action.id))
                action_id = str(action.id)
        res.update({
            'default_home_action_id': int(action_id) if action_id and action_id.isdigit() else False
        })
        return res