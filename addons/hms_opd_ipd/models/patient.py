from odoo import models, fields, api

class HmsBasePatientInherit(models.Model):
    _inherit = 'hms.base.patient'

    admission_ids = fields.One2many(
        'hms.admission',
        'patient_id',
        string='Admissions'
    )
    admission_count = fields.Integer(
        compute='_compute_admission_count',
        string='Admission Count'
    )

    def _compute_admission_count(self):
        for patient in self:
            patient.admission_count = len(patient.admission_ids)

    def action_view_admissions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient Admissions',
            'res_model': 'hms.admission',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {
                'default_patient_id': self.id,
                'default_doctor_id': self.doctor_id.id
            }
        }

    def action_view_opd_admissions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'OPD Admissions',
            'res_model': 'hms.admission',
            'view_mode': 'list,form',
            'domain': [
                ('patient_id', '=', self.id),
                ('admission_type', '=', 'opd')
            ],
            'context': {
                'default_patient_id': self.id,
                'default_admission_type': 'opd',
                'default_doctor_id': self.doctor_id.id
            }
        }

    def action_view_ipd_admissions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'IPD Admissions',
            'res_model': 'hms.admission',
            'view_mode': 'list,form',
            'domain': [
                ('patient_id', '=', self.id),
                ('admission_type', '=', 'ipd')
            ],
            'context': {
                'default_patient_id': self.id,
                'default_admission_type': 'ipd',
                'default_doctor_id': self.doctor_id.id
            }
        }