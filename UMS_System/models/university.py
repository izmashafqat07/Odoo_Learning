from odoo import models, fields, api

class OBEProgram(models.Model):
    _name = 'obe.program'
    _description = 'Academic Program'
    
    name = fields.Char(string='Program Name', required=True)
    code = fields.Char(string='Program Code', required=True)
    description = fields.Text(string='Description')
    duration = fields.Integer(string='Duration (Years)')
    active = fields.Boolean(string='Active', default=True)

class OBECourse(models.Model):
    _name = 'obe.course'
    _description = 'Course'
    
    name = fields.Char(string='Course Name', required=True)
    code = fields.Char(string='Course Code', required=True)
    program_id = fields.Many2one('obe.program', string='Program')
    credits = fields.Integer(string='Credit Hours')
    description = fields.Text(string='Course Description')
    active = fields.Boolean(string='Active', default=True)