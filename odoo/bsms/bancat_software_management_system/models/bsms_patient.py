from odoo import models, fields

class BSMSPatient(models.Model):
    _name = 'bsms.patient'
    _description = 'BSMS Patient'

    name = fields.Char(string="Name", required=True)
    contact_id = fields.Many2one('bsms.contact', string="Contact", required=True)
