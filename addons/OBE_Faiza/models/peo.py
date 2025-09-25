# -*- coding: utf-8 -*-
from lxml import etree
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PEO(models.Model):
    _name = 'obe.peo'
    _description = 'Program Educational Objective'
    _order = 'sequence, id desc'
    _rec_name = 'title'

    name = fields.Char(
        string='PEO Code',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    # Change only the label: Draft -> Unpublished
    state = fields.Selection([
        ('draft', 'Unpublished'),
        ('published', 'Published'),
    ], string='Status', default='draft', tracking=True)

    user_id = fields.Many2one('res.users', string='Created by',
                              default=lambda self: self.env.user, readonly=True)
    create_date = fields.Datetime(string='Created on', readonly=True)
    write_date = fields.Datetime(string='Last Modified', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('obe.peo') or _('New')
        return super().create(vals)

    def write(self, vals):
        # Disallow editing Published except state/sequence
        for rec in self:
            if rec.state == 'published':
                allowed = {'state', 'sequence', '__last_update'}
                if any(f not in allowed for f in vals.keys()):
                    raise UserError(_("Published PEOs cannot be edited. Only state changes are allowed."))
        return super().write(vals)

    def unlink(self):
        # Hard block deleting Published (UI also hidden when all are published)
        if any(r.state == 'published' for r in self):
            raise UserError(_("You cannot delete Published PEOs. Unpublish them first."))
        return super().unlink()

    # ------------------- Bulk actions -------------------

    def _ensure_multi_selection(self):
        if len(self) < 2:
            raise UserError(_("Select at least two records to Publish/Unpublish."))

    def action_publish_selected(self):
        if not self:
            raise UserError(_("Select records to publish."))
        self._ensure_multi_selection()
        drafts = self.filtered(lambda r: r.state == 'draft')
        if len(drafts) != len(self):
            raise UserError(_("Only Unpublished records can be published. Select Unpublished only."))
        drafts.write({'state': 'published'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_unpublish_selected(self):
        if not self:
            raise UserError(_("Select records to unpublish."))
        self._ensure_multi_selection()
        pubs = self.filtered(lambda r: r.state == 'published')
        if len(pubs) != len(self):
            raise UserError(_("Only Published records can be unpublished. Select Published only."))
        pubs.write({'state': 'draft'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    # ------------------- Single record (kept, but guarded) -------------------

    def action_publish_single(self):
        if self.state != 'draft':
            raise UserError(_("You can only publish Unpublished records."))
        self.write({'state': 'published'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_unpublish_single(self):
        if self.state != 'published':
            raise UserError(_("You can only unpublish Published records."))
        self.write({'state': 'draft'})
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.constrains('title', 'description')
    def _check_required_fields(self):
        for rec in self:
            if not (rec.title or '').strip():
                raise UserError(_("Title is required and cannot be empty."))
            if not (rec.description or '').strip():
                raise UserError(_("Description is required and cannot be empty."))

    # ------------------- Dynamic Create/Delete visibility -------------------

    @api.model
    def _all_records_published(self):
        # True if there are NO records in draft (Unpublished)
        return self.search_count([('state', '!=', 'published')]) == 0

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        If ALL records are Published:
           - hide Create and Delete in both List(Tree) and Form (delete also hides mass 'Action → Delete')
        If ANY Unpublished exists:
           - show Create/Delete again (default behavior)
        """
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        try:
            all_published = self._all_records_published()
            arch = etree.fromstring(res['arch'])

            if view_type in ('tree', 'list', 'form'):
                targets = [arch] + arch.xpath("//tree|//list|//form")
                for node in targets:
                    if all_published:
                        node.set('create', 'false')
                        node.set('delete', 'false')
                    else:
                        if 'create' in node.attrib:
                            del node.attrib['create']
                        if 'delete' in node.attrib:
                            del node.attrib['delete']

            res['arch'] = etree.tostring(arch, encoding='unicode')
        except Exception:
            # fail-open if any parsing glitch
            return res
        return res
