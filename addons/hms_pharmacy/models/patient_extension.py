from odoo import models, fields

class HmsBasePatientInherit(models.Model):
    _inherit = 'hms.base.patient'

    prescription_ids = fields.One2many('hms.prescription', 'patient_id', string='Prescriptions')
