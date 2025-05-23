from . import controllers
from . import models
import datetime

def post_init_hook(env):
    # Lấy cron job
    cron = env.ref('license.ir_cron_expiration', raise_if_not_found=False)
    if cron:
        cron.sudo().write({'nextcall': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})