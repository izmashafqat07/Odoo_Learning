from odoo import models, fields, api

class Textbook(models.Model):
    _name = 'obesystem.textbook'
    _description = 'Textbook for Course'
    _rec_name = 'display_name'
    
    name = fields.Char('Textbook Name', required=True)
    course_id = fields.Many2one('obesystem.course', string='Course')
    chapters = fields.Text('Chapters/Content')
    
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    @api.depends('name')
    def _compute_display_name(self):
        for textbook in self:
            if textbook.name:
                textbook.display_name = textbook.name
            else:
                textbook.display_name = f"Textbook-{textbook.id}"
    
    def name_get(self):
        result = []
        for textbook in self:
            result.append((textbook.id, textbook.display_name))
        return result