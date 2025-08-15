from odoo import models, fields

class HmsBaseDepartment(models.Model):
    _name = 'hms.base.department'
    _description = 'HMS Department'

    name = fields.Char(string='Department Name', required=True)
    description = fields.Text(string='Description')
    doctor_ids = fields.One2many('hms.base.doctor', 'department_id', string='Doctors')