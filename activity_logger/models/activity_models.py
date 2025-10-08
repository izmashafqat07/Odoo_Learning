from odoo import api, fields, models, tools
from odoo.http import request
from datetime import datetime
import json


class ActivitySession(models.Model):
    _name = 'activity.session'
    _description = 'User Activity Session'
    _order = 'create_date desc'

    name = fields.Char(string='Session', default=lambda self: self.env['ir.sequence'].next_by_code('activity.session') or '/')
    session_key = fields.Char(required=True, index=True)
    user_id = fields.Many2one('res.users', required=True, index=True)
    request_ids = fields.One2many('activity.request', 'session_id', string='Requests')
    create_date = fields.Datetime(readonly=True)

# Gives the “who did what via which endpoint” envelope for every request. Lets you correlate ORM changes back to a specific call.
class ActivityRequest(models.Model):
    _name = 'activity.request'
    _description = 'HTTP Request Log'
    _order = 'create_date desc'

    # computed summary like “POST /web/dataset/call_kw/...
    name = fields.Char(string='Request', compute='_compute_name', store=True)
    path = fields.Char(required=True, index=True)
    root_url = fields.Char()
    method = fields.Char()
    context_json = fields.Text(string='Context JSON')
    user_id = fields.Many2one('res.users', required=True, index=True)
    session_id = fields.Many2one('activity.session', index=True)
    change_ids = fields.One2many('activity.change', 'request_id', string='Data Changes')
    create_date = fields.Datetime(readonly=True)

    @api.depends('path', 'method')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.method or ''} {rec.path or ''}".strip()


class ActivityChange(models.Model):
    _name = 'activity.change'
    _description = 'Record Change Event'
    _order = 'create_date desc'

    # Computed summary “model method ids”.
    name = fields.Char(string='Change', compute='_compute_name', store=True)
    model_id = fields.Many2one('ir.model', index=True, ondelete='set null')
    model = fields.Char(required=True, index=True)
    res_ids_text = fields.Char(string='Record IDs (csv)')
    method = fields.Selection([('create', 'Create'), ('write', 'Write'), ('unlink', 'Delete'), ('read', 'Read'), ('export', 'Export')], required=True, index=True)
    user_id = fields.Many2one('res.users', required=True, index=True)
    request_id = fields.Many2one('activity.request', index=True)
    session_id = fields.Many2one('activity.session', index=True)
    mode = fields.Selection([('quick', 'Quick'), ('detailed', 'Detailed')], default='quick', required=True)

    # Detailed field diffs if detailed mode
    field_change_ids = fields.One2many('activity.field.change', 'change_id', string='Field Changes')
    create_date = fields.Datetime(readonly=True)

    @api.depends('model', 'method', 'res_ids_text')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.model} {rec.method} {rec.res_ids_text or ''}".strip()


class ActivityFieldChange(models.Model):
    _name = 'activity.field.change'
    _description = 'Field Level Change'
    _order = 'id desc'

    change_id = fields.Many2one('activity.change', required=True, ondelete='cascade', index=True)
    field_name = fields.Char(required=True, index=True)
    field_label = fields.Char()
    old_value_text = fields.Text()
    new_value_text = fields.Text()

    # Readable “Label: old -> new
    repr_text = fields.Text(string='Change Summary')


class ActivityReport(models.Model):
    _name = 'activity.report'
    _description = 'Activity Report'
    _auto = False

    change_id = fields.Many2one('activity.change', readonly=True)
    change_method = fields.Char(readonly=True)
    change_mode = fields.Char(readonly=True)
    model = fields.Char(readonly=True)
    res_ids_text = fields.Char(readonly=True)
    user_id = fields.Many2one('res.users', readonly=True)
    request_id = fields.Many2one('activity.request', readonly=True)
    session_id = fields.Many2one('activity.session', readonly=True)
    path = fields.Char(readonly=True)
    field_name = fields.Char(readonly=True)
    field_label = fields.Char(readonly=True)
    old_value_text = fields.Text(readonly=True)
    new_value_text = fields.Text(readonly=True)
    create_date = fields.Datetime(readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'activity_report')
        self._cr.execute(
            '''
            CREATE OR REPLACE VIEW activity_report AS (
                SELECT
                    fc.id AS id,
                    c.id AS change_id,
                    c.method AS change_method,
                    c.mode AS change_mode,
                    c.model AS model,
                    c.res_ids_text AS res_ids_text,
                    c.user_id AS user_id,
                    c.request_id AS request_id,
                    c.session_id AS session_id,
                    r.path AS path,
                    fc.field_name AS field_name,
                    fc.field_label AS field_label,
                    fc.old_value_text AS old_value_text,
                    fc.new_value_text AS new_value_text,
                    c.create_date AS create_date
                FROM activity_field_change fc
                JOIN activity_change c ON fc.change_id = c.id
                LEFT JOIN activity_request r ON c.request_id = r.id
            )
            '''
        )


