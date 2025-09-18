from odoo import models, fields, api

class Course(models.Model):
    _name = 'obesystem.course'
    _description = 'University Course'
    _rec_name = 'display_name'
    
    code = fields.Char('Course Code', required=True)
    title = fields.Char('Course Title', required=True)
    # Changed from Many2one to Many2many
    prereq_course_ids = fields.Many2many('obesystem.course', 'course_prerequisite_rel', 'course_id', 'prereq_id', string='Prerequisite Courses')
    coreq_course_ids = fields.Many2many('obesystem.course', 'course_corequisite_rel', 'course_id', 'coreq_id', string='Co-requisite Courses')
    description = fields.Text('Course Description')
    course_content = fields.Text('Course Content', 
        help="Enter course topics as comma-separated values (e.g., Introduction to Programming, Variables, Data Types)")
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