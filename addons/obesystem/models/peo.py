from odoo import models, fields, api

class PEO(models.Model):
    _name = 'obesystem.peo'
    _description = 'Program Educational Objective'
    _rec_name = 'display_name'
    
    title = fields.Char('PEO Title', required=True)
    description = fields.Text('PEO Description')
    plo_ids = fields.One2many(
        'obesystem.plo',
        'peo_id',
        string='Mapped PLOs'
    )
    
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    @api.depends('title')
    def _compute_display_name(self):
        for peo in self:
            # Check if title already contains "PEO-" format
            if peo.title and peo.title.startswith('PEO-'):
                peo.display_name = peo.title
            elif peo.title:
                peo.display_name = f"PEO-{peo.id} ({peo.title})"
            else:
                peo.display_name = f"PEO-{peo.id}"
    
    def name_get(self):
        result = []
        for peo in self:
            result.append((peo.id, peo.display_name))
        return result