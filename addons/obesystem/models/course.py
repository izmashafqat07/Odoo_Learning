from odoo import models, fields

class Course(models.Model):
    _name = 'obesystem.course'
    _description = 'University Course'
    
    code = fields.Char('Course Code', required=True)
    title = fields.Char('Course Title', required=True)
    prereq_course_id = fields.Many2one('obesystem.course', string='Prerequisite Course')
    coreq_course_id = fields.Many2one('obesystem.course', string='Co-requisite Course')
    description = fields.Text('Course Description')
    clo_ids = fields.Many2many('obesystem.clo', string='Associated CLOs')
    textbook_ids = fields.One2many('obesystem.textbook', 'course_id', string='Textbooks')
