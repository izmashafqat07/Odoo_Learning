from odoo import models, fields

class CLO(models.Model):
    _name = 'obesystem.clo'
    _description = 'Course Learning Outcome'
    
    title = fields.Char('CLO Title', required=True)
    description = fields.Text('CLO Description')
    plo_ids = fields.Many2many('obesystem.plo', string='Associated PLOs')
    course_id = fields.Many2one('obesystem.course', string='Course')

    # New Taxonomy Level field
    TAXONOMY_SELECTION = [
        ('knowledge', 'Knowledge'),
        ('comprehension', 'Comprehension'),
        ('application', 'Application'),
        ('analysis', 'Analysis'),
        ('synthesis', 'Synthesis'),
        ('evaluation', 'Evaluation'),
    ]
    taxonomy_level = fields.Selection(
        TAXONOMY_SELECTION,
        string='Taxonomy Level',
        required=True,
        default='knowledge'
    )
