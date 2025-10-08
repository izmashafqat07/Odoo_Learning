from odoo import models, fields, api

class OBEStudent(models.Model):
    _name = 'obe.student'
    _description = 'OBE Student Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Student Name', required=True)
    user_id = fields.Many2one('res.users', string='User Account')
    student_id = fields.Char(string='Student ID', required=True)
    program_id = fields.Many2one('obe.program', string='Program')
    enrollment_date = fields.Date(string='Enrollment Date')
    graduation_date = fields.Date(string='Expected Graduation')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('student_id_unique', 'unique(student_id)', 'Student ID must be unique!'),
    ]

class OBEFaculty(models.Model):
    _name = 'obe.faculty'
    _description = 'OBE Faculty Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Faculty Name', required=True)
    user_id = fields.Many2one('res.users', string='User Account')
    faculty_id = fields.Char(string='Faculty ID', required=True)
    department = fields.Char(string='Department')
    designation = fields.Char(string='Designation')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('faculty_id_unique', 'unique(faculty_id)', 'Faculty ID must be unique!'),
    ]