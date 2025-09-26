# models/clo.py
from odoo import models, fields, api, _

class CLO(models.Model):
    _name = 'obesystem.clo'
    _description = 'Course Learning Outcome'
    _rec_name = 'title'   # header/breadcrumb will use title

    title = fields.Char('CLO Title', required=True)
    description = fields.Text('CLO Description')

    # Only one PLO per CLO
    plo_id = fields.Many2one('obesystem.plo', string='Associated PLO')
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

    # id-independent, available before save
    display_name = fields.Char(compute='_compute_display_name', store=False)

    @api.depends('title')
    def _compute_display_name(self):
        for clo in self:
            clo.display_name = f"CLO ({clo.title})" if clo.title else _("New CLO")

    # Always return a non-empty label (avoids NewId_0x…)
    def name_get(self):
        res = []
        for clo in self:
            label = clo.title or _("New CLO")
            res.append((clo.id or 0, label))
        return res
