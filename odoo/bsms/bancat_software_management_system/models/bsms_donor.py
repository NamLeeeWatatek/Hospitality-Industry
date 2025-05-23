from odoo import models, fields

class BSMSDonor(models.Model):
    _name = 'bsms.donor'
    _description = 'BSMS Donor'

    name = fields.Char(string="Name", required=True)
    donor_type_id = fields.Many2one('bsms.donor.type', string="Donor Type", required=True)
    contact_id = fields.Many2one('bsms.contact', string="Contact", required=True)
