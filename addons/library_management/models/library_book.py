from odoo import models, fields, api

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string='Title', required=True)
    isbn = fields.Char(string='ISBN')
    author = fields.Char(string='Author')
    available_qty = fields.Integer(string='Available', default=1)
    description = fields.Text(string='Description')

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.author:
                name = f"{name} — {rec.author}"
            result.append((rec.id, name))
        return result