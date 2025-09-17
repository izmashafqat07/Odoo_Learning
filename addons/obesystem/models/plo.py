from odoo import models, fields

class PLO(models.Model):
    _name = 'obesystem.plo'
    _description = 'Program Learning Outcome'
    
    title = fields.Char('PLO Title', required=True)
    description = fields.Text('PLO Description')
    peo_id = fields.Many2one('obesystem.peo', string='Mapped PEO')  # Fixed: Many2one not Many2One
    clo_ids = fields.Many2many('obesystem.clo', string='Mapped CLOs')
