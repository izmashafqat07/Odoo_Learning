# models/plo.py
from odoo import models, fields, api, _

class PLO(models.Model):
    _name = 'obesystem.plo'
    _description = 'Program Learning Outcome'
    _rec_name = 'title'   # header/breadcrumb uses simple field

    title = fields.Char('PLO Title', required=True)
    description = fields.Text('PLO Description')
    peo_id = fields.Many2one('obesystem.peo', string='Mapped PEO')
    clo_ids = fields.Many2many('obesystem.clo', string='Mapped CLOs')

    # Make it available before save & avoid id dependency
    display_name = fields.Char(compute='_compute_display_name', store=False)

    @api.depends('title')
    def _compute_display_name(self):
        for plo in self:
            plo.display_name = plo.title or _("New PLO")

    # Always return a non-empty label (prevents NewId_0x…)
    def name_get(self):
        res = []
        for plo in self:
            label = plo.title or _("New PLO")
            res.append((plo.id or 0, label))
        return res
