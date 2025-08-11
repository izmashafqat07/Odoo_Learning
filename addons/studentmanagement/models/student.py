from odoo import models, fields, api
from datetime import date

class Student(models.Model):
    _name = 'school.student'
    _description = 'Student'

    name = fields.Char(string='Full Name', required=True)
    roll_number = fields.Char(string='Roll Number', required=True)
    dob = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    class_name = fields.Char(string='Class / Grade')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    notes = fields.Text(string='Notes')

    @api.depends('dob')
    def _compute_age(self):
        for rec in self:
            if rec.dob:
                today = date.today()
                # compute age in years
                try:
                    born = rec.dob
                    # born is a date object (odoo returns date for fields.Date)
                    years = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
                    rec.age = years
                except Exception:
                    rec.age = 0
            else:
                rec.age = 0
