# -*- coding: utf-8 -*-
from lxml import etree
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class PEO(models.Model):
    _name = 'obe.peo'
    _description = 'Program Educational Objective'
    _order = 'sequence, id desc'
    _rec_name = 'title'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='PEO Code', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    title = fields.Char(string='Title', required=True, tracking=True)
    description = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    # Draft label -> Unpublished (value remains 'draft')
    state = fields.Selection(
        [('draft', 'Unpublished'), ('published', 'Published')],
        string='Status', default='draft', tracking=True
    )

    user_id = fields.Many2one('res.users', string='Created by',
                              default=lambda self: self.env.user, readonly=True)
    create_date = fields.Datetime(string='Created on', readonly=True)
    write_date = fields.Datetime(string='Last Modified', readonly=True)

    # ---------- helpers ----------
    @api.model
    def _all_records_published(self):
        total = self.search_count([])
        if total == 0:
            return False
        return self.search_count([('state', '!=', 'published')]) == 0

    # ---------- stop form from opening when all published ----------
    @api.model
    def default_get(self, fields_list):
        if self._all_records_published():
            raise UserError(_("All PEOs are Published. Unpublish to create a new record."))
        return super().default_get(fields_list)

    # ---------- dynamic rights so UI hides Create/Delete at list/form ----------
    def check_access_rights(self, operation, raise_exception=True):
        has_rights = super().check_access_rights(operation, raise_exception=raise_exception)
        if not has_rights:
            return has_rights
        if operation in ('create', 'unlink') and self._all_records_published():
            verb = _("create") if operation == 'create' else _("delete")
            msg = _("All PEOs are Published. Unpublish at least one PEO to %s records.") % verb
            if raise_exception:
                raise AccessError(msg)
            return False
        return has_rights

    # ---------- hard safety ----------
    @api.model
    def create(self, vals):
        if self._all_records_published():
            raise UserError(_("All PEOs are Published. Unpublish at least one PEO to create a new record."))
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('obe.peo') or _('New')
        return super().create(vals)

    def write(self, vals):
        for rec in self:
            if rec.state == 'published':
                allowed = {'state', 'sequence', '__last_update'}
                for f in vals.keys():
                    if f not in allowed:
                        raise UserError(_("Published PEOs cannot be edited. Only state changes are allowed."))
        return super().write(vals)

    def unlink(self):
        if self._all_records_published():
            raise UserError(_("All PEOs are Published. Unpublish to delete records."))
        for rec in self:
            if rec.state == 'published':
                raise UserError(_("You cannot delete Published PEOs. Unpublish them first."))
        return super().unlink()

    # ---------- bulk actions (buttons call these) ----------
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

    # ---------- single record ----------
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

    # ---------- UI attribute toggle (extra safety) ----------
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
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
                        node.attrib.pop('create', None)
                        node.attrib.pop('delete', None)
            res['arch'] = etree.tostring(arch, encoding='unicode')
        except Exception:
            return res
        return res
