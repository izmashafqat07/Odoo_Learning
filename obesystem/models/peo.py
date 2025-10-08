# -*- coding: utf-8 -*-
from lxml import etree
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class PEO(models.Model):
    _name = 'obesystem.peo'
    _description = 'Program Educational Objective'
    _order = 'id desc'
    _rec_name = 'title'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- fields ---
    title = fields.Char('PEO Title', required=True, tracking=True)
    description = fields.Text('PEO Description', required=True)

    state = fields.Selection(
        [('draft', 'Unpublished'), ('published', 'Published')],
        string='Status', default='draft', tracking=True
    )
    document_id = fields.Many2one(
        'obesystem.document', string='Reference Document', tracking=True,
        help="Under which document/policy this PEO falls"
    )
    document_note = fields.Char('Document Note / Clause', help="Optional clause/section reference")

    user_id = fields.Many2one('res.users', string='Created by',
                              default=lambda self: self.env.user, readonly=True)

    display_name = fields.Char(compute='_compute_display_name', store=False)

    @api.depends('title')
    def _compute_display_name(self):
        for peo in self:
            peo.display_name = f"PEO ({peo.title})" if peo.title else _("New ")

    def name_get(self):
        return [(rec.id or 0, rec.title or _("New")) for rec in self]

    # ---------- helpers ----------
    @api.model
    def _all_records_published(self):
        # True only if there is at least 1 record AND no record is != published
        total = self.sudo().search_count([])
        if total == 0:
            return False
        return self.sudo().search_count([('state', '!=', 'published')]) == 0

    # ---------- stop form from opening when all published ----------
    @api.model
    def default_get(self, fields_list):
        if self._all_records_published():
            raise UserError(_("All PEOs are Published. Unpublish to create a new record."))
        return super().default_get(fields_list)
    
    # ---------- server-side safety ----------
    def check_access_rights(self, operation, raise_exception=True):
        has_rights = super().check_access_rights(operation, raise_exception=raise_exception)
        if not has_rights:
            return has_rights
        if operation in ('create', 'unlink') and self._all_records_published():
            if raise_exception:
                verb = _("create") if operation == 'create' else _("delete")
                raise AccessError(_("All PEOs are Published. Unpublish at least one PEO to %s records.") % verb)
            return False
        return has_rights

    @api.model
    def create(self, vals):
        if self._all_records_published():
            raise UserError(_("All PEOs are Published. Unpublish at least one PEO to create a new record."))
        return super().create(vals)

    def write(self, vals):
        for rec in self:
            if rec.state == 'published':
                allowed = {'state', '__last_update'}
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

    # ---------- document checks before publish ----------
    def _check_document_before_publish(self):
        missing = self.filtered(lambda r: not r.document_id)
        if missing:
            raise UserError(_("Please select a Reference Document before publishing.\nMissing on: %s")
                            % ", ".join(missing.mapped('title')))
        not_pub = self.filtered(lambda r: r.document_id.state != 'published')
        if not_pub:
            raise UserError(_("Reference Document must be Published before publishing PEOs.\nFix for: %s")
                            % ", ".join(not_pub.mapped('title')))
    

    # ---------- bulk actions ----------
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
        drafts._check_document_before_publish()
        drafts.write({'state': 'published'})
        for rec in drafts:
            rec.message_post(body=_("PEO published under document: %s") % (rec.document_id.name or "-"))
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_unpublish_selected(self):
        if not self:
            raise UserError(_("Select records to unpublish."))
        self._ensure_multi_selection()
        pubs = self.filtered(lambda r: r.state == 'published')
        if len(pubs) != len(self):
            raise UserError(_("Only Published records can be unpublished. Select Published only."))
        pubs.write({'state': 'draft'})
        for rec in pubs:
            rec.message_post(body=_("PEO unpublished."))
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    # ---------- single record ----------
    def action_publish_single(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_("You can only publish Unpublished records."))
        self._check_document_before_publish()
        self.write({'state': 'published'})
        self.message_post(body=_("PEO published under document: %s") % (self.document_id.name,))
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_unpublish_single(self):
        self.ensure_one()
        if self.state != 'published':
            raise UserError(_("You can only unpublish Published records."))
        self.write({'state': 'draft'})
        self.message_post(body=_("PEO unpublished."))
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    # ======== UI TOGGLES ========

    def _apply_create_delete_toggle_to_arch(self, arch_xml, enable):
        """enable=True  => show create/delete
           enable=False => hide create/delete
        """
        if not arch_xml:
            return arch_xml
        root = etree.fromstring(arch_xml)
        targets = [root] + root.xpath("//tree|//list|//form")
        for node in targets:
            if enable:
                node.attrib.pop('create', None)
                node.attrib.pop('delete', None)
            else:
                node.set('create', 'false')
                node.set('delete', 'false')
        return etree.tostring(root, encoding='unicode')

    def _apply_flags_toggle(self, flags, enable):
        """flags: dict from view payload"""
        flags = (flags or {}).copy()
        if enable:
            flags.pop('create', None)
            flags.pop('delete', None)
        else:
            flags['create'] = False
            flags['delete'] = False
        return flags

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Single view fetch — toggle here too"""
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        try:
            # show buttons ONLY if NOT all published
            enable = not self._all_records_published()

            # arch
            if res.get('arch') and view_type in ('tree', 'list', 'form'):
                res['arch'] = self._apply_create_delete_toggle_to_arch(res['arch'], enable)

            # flags
            res['flags'] = self._apply_flags_toggle(res.get('flags'), enable)

        except Exception:
            return res
        return res

    @api.model
    def get_views(self, views, options=None):
        """Multi view fetch (newer paths)"""
        res = super().get_views(views, options=options)
        try:
            enable = not self._all_records_published()
            fv = res.get('fields_views') or {}
            for key, payload in fv.items():
                # flags
                payload['flags'] = self._apply_flags_toggle(payload.get('flags'), enable)
                # arch
                if payload.get('arch'):
                    payload['arch'] = self._apply_create_delete_toggle_to_arch(payload['arch'], enable)
            res['fields_views'] = fv
        except Exception:
            return res
        return res

    @api.model
    def load_views(self, views, options=None):
        """Multi view fetch (older paths / some builds)"""
        res = super().load_views(views, options=options)
        try:
            enable = not self._all_records_published()
            fv = res.get('fields_views') or {}
            for key, payload in fv.items():
                # flags
                payload['flags'] = self._apply_flags_toggle(payload.get('flags'), enable)
                # arch
                if payload.get('arch'):
                    payload['arch'] = self._apply_create_delete_toggle_to_arch(payload['arch'], enable)
            res['fields_views'] = fv
        except Exception:
            return res
        return res
