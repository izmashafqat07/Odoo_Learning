from odoo import models, fields

# Program Educational Objective (PEO)
class PEO(models.Model):
    _name = 'obesystem.peo'
    _description = 'Program Educational Objective'
    
    title = fields.Char('PEO Title', required=True)
    description = fields.Text('PEO Description')
    plo_ids = fields.Many2many('obesystem.plo', string='Mapped PLOs')

# Program Learning Outcome (PLO)
class PLO(models.Model):
    _name = 'obesystem.plo'
    _description = 'Program Learning Outcome'
    
    title = fields.Char('PLO Title', required=True)
    description = fields.Text('PLO Description')
    peo_ids = fields.Many2many('obesystem.peo', string='Mapped PEOs')
    clo_ids = fields.Many2many('obesystem.clo', string='Mapped CLOs')

# Course Learning Outcome (CLO)
class CLO(models.Model):
    _name = 'obesystem.clo'
    _description = 'Course Learning Outcome'
    
    title = fields.Char('CLO Title', required=True)
    description = fields.Text('CLO Description')
    plo_ids = fields.Many2many('obesystem.plo', string='Associated PLOs')
    course_id = fields.Many2one('obesystem.course', string='Course')

# University Course Model
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

# Textbook Model
class Textbook(models.Model):
    _name = 'obesystem.textbook'
    _description = 'Textbook for Course'
    
    name = fields.Char('Textbook Name', required=True)
    course_id = fields.Many2one('obesystem.course', string='Course')
    chapters = fields.Text('Chapters/Content')
