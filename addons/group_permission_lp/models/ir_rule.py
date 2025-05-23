from odoo import models, fields, api


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    def delete_old_rules(self):
        """Delete old rules that are not in the new rule list."""
        # Get the current rules
        current_rules = self.search([('name', 'ilike', 'Restrict Stock Picking')])
        current_rules.unlink()