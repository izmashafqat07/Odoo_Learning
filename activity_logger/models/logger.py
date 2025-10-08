from odoo import api, models
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class ActivityLogger(models.AbstractModel):
    _name = 'activity.logger'
    _description = 'Activity Logger Service'

    @api.model
    def ensure_http_envelope(self):
        """Ensure request/session records exist and are stashed on the request object.
        Returns (request_record or None, session_record or None).
        """
        if not request:
            return None, None
        ActivityRequest = self.env['activity.request'].sudo()
        ActivitySession = self.env['activity.session'].sudo()
        uid = request.uid or self.env.uid
        try:
            req_id = getattr(request, '_activity_request_id', None)
            sess_id = getattr(request, '_activity_session_id', None)
            if req_id and sess_id:
                return ActivityRequest.browse(req_id), ActivitySession.browse(sess_id)
            sid = request.httprequest.session.sid
            session = ActivitySession.search([('session_key', '=', sid), ('user_id', '=', uid)], limit=1)
            if not session:
                session = ActivitySession.create({'session_key': sid, 'user_id': uid})
            req_rec = ActivityRequest.create({
                'path': request.httprequest.path,
                'root_url': request.httprequest.host_url,
                'method': request.httprequest.method,
                'user_id': uid,
                'session_id': session.id,
                'context_json': str(getattr(request, 'context', {}) or {}),
            })
            setattr(request, '_activity_request_id', req_rec.id)
            setattr(request, '_activity_session_id', session.id)
            _logger.debug('activity_logger: ensure_http_envelope created request_id=%s session_id=%s', req_rec.id, session.id)
            return req_rec, session
        except Exception:
            _logger.exception('activity_logger: ensure_http_envelope failed')
            return None, None

    @api.model
    def log_change(self, model_name, method_name, res_ids, before_values=None, after_values=None, rule=None):
        _logger.debug('activity_logger: log_change start model=%s method=%s ids=%s rule=%s', model_name, method_name, res_ids, getattr(rule, 'id', None))
        ActivityChange = self.env['activity.change'].sudo()
        ActivityFieldChange = self.env['activity.field.change'].sudo()
        ActivityRequest = self.env['activity.request'].sudo()
        ActivitySession = self.env['activity.session'].sudo()

        uid = request.uid if request and request.uid else self.env.uid

        # Link to existing request/session if already created by ir.http
        req_rec = None
        session = None
        if request:
            try:
                req_id = getattr(request, '_activity_request_id', None)
                sess_id = getattr(request, '_activity_session_id', None)
                if sess_id:
                    session = ActivitySession.browse(sess_id)
                if req_id:
                    req_rec = ActivityRequest.browse(req_id)
            except Exception:
                req_rec = None
                session = None

        # If there is no HTTP context (cron, shell, tests), create minimal context lazily
        if not req_rec and request:
            req_rec, session = self.ensure_http_envelope()

        change = ActivityChange.create({
            'model_id': self.env['ir.model']._get_id(model_name) if model_name else False,
            'model': model_name,
            'res_ids_text': ','.join(map(str, res_ids)) if res_ids else '',
            'method': method_name,
            'user_id': uid,
            'request_id': req_rec.id if req_rec else False,
            'session_id': session.id if session else False,
            'mode': rule.mode if rule else 'quick',
        })
        _logger.debug('activity_logger: change created id=%s', change.id)

        if rule and rule.mode == 'detailed' and before_values is not None and after_values is not None:
            excluded_fields = set(rule.excluded_field_ids.mapped('name'))
            for record_id, field_map in after_values.items():
                before_map = before_values.get(record_id, {})
                for field_name, new_val in field_map.items():
                    if field_name in excluded_fields:
                        continue
                    old_val = before_map.get(field_name)
                    if old_val == new_val:
                        continue
                    label = self.env[model_name]._fields.get(field_name).string if field_name in self.env[model_name]._fields else field_name
                    ActivityFieldChange.create({
                        'change_id': change.id,
                        'field_name': field_name,
                        'field_label': label,
                        'old_value_text': str(old_val),
                        'new_value_text': str(new_val),
                        'repr_text': f"{label}: {old_val} -> {new_val}",
                    })

        _logger.debug('activity_logger: log_change done id=%s', change.id)

        return change


