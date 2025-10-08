from odoo import models, fields

class HmsBaseDoctor(models.Model):
    # _inherit = 'res.partner'

    _name = 'hms.base.doctor'
    _description = 'HMS Doctor'

    name = fields.Char(string='Doctor Name', required=True)
    specialization = fields.Char(string='Specialization')
    department_id = fields.Many2one('hms.base.department', string='Department')
    is_doctor = fields.Boolean(string='Is Doctor', default=True)
    patient_ids = fields.One2many('hms.base.patient', 'doctor_id', string='Patients')