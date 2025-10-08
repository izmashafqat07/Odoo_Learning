from odoo import models, fields, api

class UniversityStaffType(models.Model):
    _name = 'university.staff.type'
    _description = 'University Staff Type'
    
    name = fields.Char(string='Staff Type', required=True)
    description = fields.Text(string='Description')
    
  
    active = fields.Boolean(string='Active', default=True)