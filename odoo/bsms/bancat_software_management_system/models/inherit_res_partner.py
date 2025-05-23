from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string="Is Patient", default=False, invisible=True)
    is_donor = fields.Boolean(string="Is Donor", default=False, invisible=True)

    donor_type_id = fields.Many2one(
        'bsms.donor.type', 
        string='Donor Type',
        help="Select the type of donor."
    )

    @api.model
    def create(self, vals):
        partner = super(ResPartnerInherit, self).create(vals)
        partner._sync_to_bsms()
        return partner

    def write(self, vals):
        res = super(ResPartnerInherit, self).write(vals)
        if 'is_patient' in vals or 'is_donor' in vals:
            self._sync_to_bsms()
        return res

    def _sync_to_bsms(self):
        for partner in self:
            try:
                # Sync to bsms.contact
                contact_vals = {
                    'name': partner.name,
                    'is_patient': partner.is_patient,
                    'is_donor': partner.is_donor,
                }
                contact = self.env['bsms.contact'].search([('id', '=', partner.id)], limit=1)
                if contact:
                    contact.write(contact_vals)
                else:
                    contact = self.env['bsms.contact'].create(contact_vals)

                # Sync to bsms.patient if is_patient is True
                if partner.is_patient:
                    patient_vals = {
                        'name': partner.name,
                        'contact_id': contact.id,
                    }
                    patient = self.env['bsms.patient'].search([('contact_id', '=', contact.id)], limit=1)
                    if patient:
                        patient.write(patient_vals)
                    else:
                        self.env['bsms.patient'].create(patient_vals)

                # Sync to bsms.donor if is_donor is True
                if partner.is_donor:
                    if not partner.donor_type_id:
                        raise ValidationError(_("Donor Type must be selected for donors."))
                    donor_vals = {
                        'name': partner.name,
                        'donor_type_id': partner.donor_type_id.id,
                        'contact_id': contact.id,
                    }
                    donor = self.env['bsms.donor'].search([('contact_id', '=', contact.id)], limit=1)
                    if donor:
                        donor.write(donor_vals)
                    else:
                        self.env['bsms.donor'].create(donor_vals)

            except Exception as e:
                _logger.error(f"Error syncing partner {partner.id}: {str(e)}")                      

