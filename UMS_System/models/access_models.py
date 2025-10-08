from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    role_type = fields.Selection([
        ('admin', 'University Admin'),
        ('coordinator', 'OBE Coordinator'),
        ('faculty', 'Faculty Member'),
        ('student', 'Student')
    ], string='Role Type', default='faculty')
    
    faculty_id = fields.Many2one('obe.faculty', string='Faculty Profile')
    student_id = fields.Many2one('obe.student', string='Student Profile')