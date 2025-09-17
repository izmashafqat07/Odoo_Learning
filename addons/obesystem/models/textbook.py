from odoo import models, fields

class Textbook(models.Model):
    _name = 'obesystem.textbook'
    _description = 'Textbook for Course'
    
    name = fields.Char('Textbook Name', required=True)
    course_id = fields.Many2one('obesystem.course', string='Course')
    chapters = fields.Text('Chapters/Content')
