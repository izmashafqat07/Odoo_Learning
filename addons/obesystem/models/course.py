from odoo import models, fields, api

class Course(models.Model):
    _name = 'obesystem.course'
    _description = 'University Course'
    _rec_name = 'display_name'
    
    code = fields.Char('Course Code', required=True)
    title = fields.Char('Course Title', required=True)
    prereq_course_id = fields.Many2one('obesystem.course', string='Prerequisite Course')
    coreq_course_id = fields.Many2one('obesystem.course', string='Co-requisite Course')
    description = fields.Text('Course Description')
    clo_ids = fields.Many2many('obesystem.clo', string='Associated CLOs')
    textbook_ids = fields.One2many('obesystem.textbook', 'course_id', string='Textbooks')
    
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    @api.depends('code', 'title')
    def _compute_display_name(self):
        for course in self:
            if course.code and course.title:
                course.display_name = f"{course.code} - {course.title}"
            elif course.code:
                course.display_name = course.code
            elif course.title:
                course.display_name = course.title
            else:
                course.display_name = f"Course-{course.id}"
    
    def name_get(self):
        result = []
        for course in self:
            result.append((course.id, course.display_name))
        return result