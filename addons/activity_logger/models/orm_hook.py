from odoo import models, api
from odoo.http import request
from odoo.models import BaseModel
import logging

_logger = logging.getLogger(__name__)


def _get_current_user_and_request(env):
    if request and hasattr(request, 'uid') and request.uid:
        return request.uid, request
    return env.uid, None


class AuditedModel(models.AbstractModel):
    _name = 'activity.audited.mixin'
    _description = 'Audited Model Mixin'

    def _activity_get_rule(self, method_name):
        Rule = self.env['activity.rule']
        user_id, _ = _get_current_user_and_request(self.env)
        # Try cache on env for performance
        rules = Rule.search([('active', '=', True), ('model', '=', self._name)])
        for rule in rules:
            if rule.applies_to(self._name, method_name, user_id):
                return rule
        return None

    def _activity_log_change(self, method_name, res_ids, before_values=None, after_values=None, rule=None):
        ActivityChange = self.env['activity.change'].sudo()
        ActivityFieldChange = self.env['activity.field.change'].sudo()
        ActivityRequest = self.env['activity.request'].sudo()
        ActivitySession = self.env['activity.session'].sudo()

        uid, http_req = _get_current_user_and_request(self.env)
        session = None
        req_rec = None

        if http_req:
            sid = http_req.httprequest.session.sid
            # Ensure session
            session = ActivitySession.search([('session_key', '=', sid), ('user_id', '=', uid)], limit=1)
            if not session:
                session = ActivitySession.create({
                    'session_key': sid,
                    'user_id': uid,
                })
            # Create request log
            context_json = {}
            try:
                context_json = http_req.context or {}
            except Exception:
                context_json = {}
            req_rec = ActivityRequest.create({
                'path': http_req.httprequest.path,
                'root_url': http_req.httprequest.host_url,
                'method': http_req.httprequest.method,
                'user_id': uid,
                'session_id': session.id,
                'context_json': str(context_json),
            })

        change = ActivityChange.create({
            'model_id': self.env['ir.model']._get_id(self._name),
            'model': self._name,
            'res_ids_text': ','.join(map(str, res_ids)) if res_ids else '',
            'method': method_name,
            'user_id': uid,
            'request_id': req_rec.id if req_rec else False,
            'session_id': session.id if session else False,
            'mode': rule.mode if rule else 'quick',
        })

        if rule and rule.mode == 'detailed' and before_values and after_values:
            excluded_fields = set(rule.excluded_field_ids.mapped('name'))
            for record_id, field_map in after_values.items():
                before_map = before_values.get(record_id, {})
                for field_name, new_val in field_map.items():
                    if field_name in excluded_fields:
                        continue
                    old_val = before_map.get(field_name)
                    if old_val == new_val:
                        continue
                    field = self._fields.get(field_name)
                    label = field.string if field else field_name
                    ActivityFieldChange.create({
                        'change_id': change.id,
                        'field_name': field_name,
                        'field_label': label,
                        'old_value_text': str(old_val),
                        'new_value_text': str(new_val),
                        'repr_text': f"{label}: {old_val} -> {new_val}",
                    })

        return change

    @api.model_create_multi
    def create(self, vals_list):
        rule = self._activity_get_rule('create')
        records = super().create(vals_list)
        if rule:
            self._activity_log_change('create', records.ids, after_values={rec.id: vals for rec, vals in zip(records, vals_list)}, rule=rule)
        return records

    def write(self, vals):
        rule = self._activity_get_rule('write')
        before = {}
        if rule and rule.mode == 'detailed':
            for rec in self:
                before[rec.id] = {k: rec[k] for k in vals.keys() if k in rec}
        result = super().write(vals)
        if rule:
            after = None
            if rule.mode == 'detailed':
                after = {}
                for rec in self:
                    after[rec.id] = {k: rec[k] for k in vals.keys() if k in rec}
            self._activity_log_change('write', self.ids, before_values=before, after_values=after, rule=rule)
        return result

    def unlink(self):
        rule = self._activity_get_rule('unlink')
        res_ids = self.ids
        result = super().unlink()
        if rule:
            self._activity_log_change('unlink', res_ids, rule=rule)
        return result


def patch_orm_methods():
    """Monkey patch BaseModel to route ORM calls through our mixin logic for all models.
    This guarantees tracking even when specific models don't inherit the mixin.
    """
    if getattr(BaseModel, '_activity_patched', False):
        return

    original_create = BaseModel.create
    original_write = BaseModel.write
    original_unlink = BaseModel.unlink

    def _get_rule(self, method):
        try:
            Rule = self.env['activity.rule']
            user_id = request.uid if request and request.uid else self.env.uid
            rules = Rule.search([('active', '=', True), ('model', '=', self._name)])
            _logger.debug('activity_logger: resolving rule for model=%s method=%s user=%s -> candidates=%s', self._name, method, user_id, rules.ids)
            for r in rules:
                if r.applies_to(self._name, method, user_id):
                    _logger.debug('activity_logger: rule matched id=%s mode=%s', r.id, r.mode)
                    return r
        except Exception:
            _logger.exception('activity_logger: rule resolution failed for model=%s method=%s', self._name, method)
            return None
        return None

    def patched_create(self, vals_list):
        rule = _get_rule(self, 'create')
        _logger.debug('activity_logger: patched_create model=%s count=%s rule=%s', self._name, len(vals_list), getattr(rule, 'id', None))
        records = original_create(self, vals_list)
        if rule:
            after_map = {rec.id: vals for rec, vals in zip(records, vals_list)}
            try:
                self.env['activity.logger'].log_change(self._name, 'create', records.ids, after_values=after_map, rule=rule)
            except Exception:
                _logger.exception('activity_logger: log_change failed on create model=%s ids=%s', self._name, records.ids)
        return records

    def patched_write(self, vals):
        rule = _get_rule(self, 'write')
        _logger.debug('activity_logger: patched_write model=%s ids=%s rule=%s vals_keys=%s', self._name, self.ids, getattr(rule, 'id', None), list(vals.keys()))
        before = {}
        if rule and rule.mode == 'detailed':
            for rec in self:
                before[rec.id] = {k: rec[k] for k in vals.keys() if k in rec}
        result = original_write(self, vals)
        if rule:
            after = None
            if rule.mode == 'detailed':
                after = {rec.id: {k: rec[k] for k in vals.keys() if k in rec} for rec in self}
            try:
                self.env['activity.logger'].log_change(self._name, 'write', self.ids, before_values=before, after_values=after, rule=rule)
            except Exception:
                _logger.exception('activity_logger: log_change failed on write model=%s ids=%s', self._name, self.ids)
        return result

    def patched_unlink(self):
        rule = _get_rule(self, 'unlink')
        _logger.debug('activity_logger: patched_unlink model=%s ids=%s rule=%s', self._name, self.ids, getattr(rule, 'id', None))
        res_ids = self.ids
        result = original_unlink(self)
        if rule:
            try:
                self.env['activity.logger'].log_change(self._name, 'unlink', res_ids, rule=rule)
            except Exception:
                _logger.exception('activity_logger: log_change failed on unlink model=%s ids=%s', self._name, res_ids)
        return result

    BaseModel.create = patched_create
    BaseModel.write = patched_write
    BaseModel.unlink = patched_unlink
    BaseModel._activity_patched = True
    _logger.info('activity_logger: BaseModel patched for create/write/unlink')

# Apply patch at import time to ensure activation even if post_load is not called
try:
    patch_orm_methods()
except Exception:
    _logger.exception('activity_logger: failed to patch BaseModel at import time')


