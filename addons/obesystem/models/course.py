# models/course.py
from odoo import models, fields, api, _

class Course(models.Model):
    _name = 'obesystem.course'
    _description = 'University Course'
    _rec_name = 'title'   # header/breadcrumb uses a simple field

    code = fields.Char('Course Code', required=True)
    title = fields.Char('Course Title', required=True)

    # Many2many prereqs/coreqs
    prereq_course_ids = fields.Many2many(
        'obesystem.course', 'course_prerequisite_rel', 'course_id', 'prereq_id',
        string='Prerequisite Courses'
    )
    coreq_course_ids = fields.Many2many(
        'obesystem.course', 'course_corequisite_rel', 'course_id', 'coreq_id',
        string='Co-requisite Courses'
    )

    description = fields.Text('Course Description')
    course_content = fields.Text(
        'Course Content',
        help="Enter course topics as comma-separated values (e.g., Introduction to Programming, Variables, Data Types)"
    )
    clo_ids = fields.Many2many('obesystem.clo', string='Associated CLOs')
    textbook_ids = fields.One2many('obesystem.textbook', 'course_id', string='Textbooks')

    # Make it available before save & avoid id dependency
    display_name = fields.Char(compute='_compute_display_name', store=False)

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
                course.display_name = _("New Course")

    # Always return a non-empty label (prevents NewId_0x…)
    def name_get(self):
        res = []
        for course in self:
            if course.code and course.title:
                label = f"{course.code} - {course.title}"
            else:
                label = course.title or course.code or _("New Course")
            res.append((course.id or 0, label))
        return res
