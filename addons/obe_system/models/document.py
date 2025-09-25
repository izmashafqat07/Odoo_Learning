# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ObeDocument(models.Model):
    _name = 'obe.document'
    _description = 'Reference Document'
    _order = 'sequence, id desc'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Title', required=True, tracking=True)
    reference = fields.Char('Reference / Number', tracking=True)
    version = fields.Char('Version', default='1.0', tracking=True)
    type = fields.Selection([
        ('policy', 'Policy'),
        ('manual', 'Manual'),
        ('regulation', 'Regulation'),
        ('curriculum', 'Curriculum'),
        ('other', 'Other'),
    ], string='Type', default='policy', tracking=True)
    effective_date = fields.Date('Effective Date', tracking=True)
    sequence = fields.Integer(default=10)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
    ], default='draft', string='Status', tracking=True)

    attachment_ids = fields.Many2many(
        'ir.attachment', 'obe_document_ir_attachment_rel', 'document_id', 'attachment_id',
        string='Files'
    )

    def action_publish(self):
        for rec in self:
            if not rec.attachment_ids:
                raise UserError(_("Add at least one file/attachment before publishing the document."))
            rec.state = 'published'

    def action_unpublish(self):
        self.write({'state': 'draft'})
