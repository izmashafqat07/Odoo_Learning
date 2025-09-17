from odoo import models, fields

class PEO(models.Model):
    _name = 'obesystem.peo'
    _description = 'Program Educational Objective'
    
    title = fields.Char('PEO Title', required=True)
    description = fields.Text('PEO Description')
    plo_ids = fields.One2many(
        'obesystem.plo',   # fix the relation
        'peo_id',
        string='Mapped PLOs'
    )
