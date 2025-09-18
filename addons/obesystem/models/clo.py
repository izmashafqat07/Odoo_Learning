from odoo import models, fields, api

class CLO(models.Model):
    _name = 'obesystem.clo'
    _description = 'Course Learning Outcome'
    _rec_name = 'display_name'
    
    title = fields.Char('CLO Title', required=True)
    description = fields.Text('CLO Description')
    plo_ids = fields.Many2many('obesystem.plo', string='Associated PLOs')
    course_id = fields.Many2one('obesystem.course', string='Course')

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
    
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    @api.depends('title')
    def _compute_display_name(self):
        for clo in self:
            # Check if title already contains "CLO-" format
            if clo.title and clo.title.startswith('CLO-'):
                clo.display_name = clo.title
            elif clo.title:
                clo.display_name = f"CLO-{clo.id} ({clo.title})"
            else:
                clo.display_name = f"CLO-{clo.id}"
    
    def name_get(self):
        result = []
        for clo in self:
            result.append((clo.id, clo.display_name))
        return result