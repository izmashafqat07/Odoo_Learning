from odoo import models, fields, api

class PLO(models.Model):
    _name = 'obesystem.plo'
    _description = 'Program Learning Outcome'
    _rec_name = 'title'
    
    
    
    title = fields.Char('PLO Title', required=True)
    description = fields.Text('PLO Description')
    peo_id = fields.Many2one('obesystem.peo', string='Mapped PEO')
    clo_ids = fields.Many2many('obesystem.clo', string='Mapped CLOs')
    
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    @api.depends('title')
    def _compute_display_name(self):
        for plo in self:
            if plo.title:
                # Format: "PLO-1 Engineering Knowledge" (without the redundant part)
                plo.display_name = f"{(plo.title)}"
            else:
                plo.display_name = f"PLO-{plo.id}"
    
    def name_get(self):
        result = []
        for plo in self:
            result.append((plo.id, plo.display_name))
        return result