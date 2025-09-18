from odoo import models, fields, api

class PLO(models.Model):
    _name = 'obesystem.plo'
    _description = 'Program Learning Outcome'
    _rec_name = 'display_name'
    
    title = fields.Char('PLO Title', required=True)
    description = fields.Text('PLO Description')
    peo_id = fields.Many2one('obesystem.peo', string='Mapped PEO')
    clo_ids = fields.Many2many('obesystem.clo', string='Mapped CLOs')
    
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    @api.depends('title')
    def _compute_display_name(self):
        for plo in self:
            # Check if title already contains "PLO-" format
            if plo.title and plo.title.startswith('PLO-'):
                plo.display_name = plo.title
            elif plo.title:
                plo.display_name = f"PLO-{plo.id} ({plo.title})"
            else:
                plo.display_name = f"PLO-{plo.id}"
    
    def name_get(self):
        result = []
        for plo in self:
            result.append((plo.id, plo.display_name))
        return result