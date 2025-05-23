from . import model
from odoo import api, SUPERUSER_ID

# def pre_init_hook(env):
#     param_model = env['ir.config_parameter'].sudo()
#     action_id = param_model.get_param('default_home_discuss.default_home_action_id')
#     if not action_id:
#         action = env.ref('mail.action_discuss', raise_if_not_found=False)
#         if action:
#             action_id = str(action.id)
#             param_model.set_param('default_home_discuss.default_home_action_id', action_id)

#     if action_id:
#         env['res.users'].sudo().search([]).write({'action_id': int(action_id)})
#         env['ir.default'].sudo().set('res.users', 'action_id', int(action_id))

def uninstall_hook(env):
    env['res.users'].sudo().search([]).write({'action_id': False})