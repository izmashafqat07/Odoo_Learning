from odoo import models, fields



class HmsBasePatient(models.Model):
    # _inherit = 'res.partner'
    
    _name = 'hms.base.patient'
    _description = 'HMS Patient'

    name = fields.Char(string='Patient Name', required=True)
    is_patient = fields.Boolean(string='Is Patient', default=False)
    # patient_id = fields.Char(string='Patient ID', readonly=True, copy=False)
    dob = fields.Date(string='Date of Birth')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender')
    blood_type = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'),
        ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'),
        ('o+', 'O+'), ('o-', 'O-')
    ], string='Blood Type')
    allergies = fields.Text(string='Allergies')
    emergency_contact = fields.Char(string='Emergency Contact')
    doctor_id = fields.Many2one('hms.base.doctor', string='Assigned Doctor', domain=[('is_doctor', '=', True)]) 