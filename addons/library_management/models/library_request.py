from odoo import models, fields

class LibraryRequest(models.Model):
    _name = 'library.request'
    _description = 'Library Book Request'

    name = fields.Char('Name', required=True)
    email = fields.Char('Email')
    book_title = fields.Char('Book Title', required=True)
    notes = fields.Text('Notes')
    state = fields.Selection([
        ('new', 'New'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
    ], default='new')
