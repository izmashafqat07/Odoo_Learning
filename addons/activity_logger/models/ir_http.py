from odoo import models
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def _activity_log_request(self):
        try:
            if not request:
                return None
            env = request.env
            uid = request.uid or env.uid
            if not uid:
                return None
            ActivityRequest = env['activity.request'].sudo()
            ActivitySession = env['activity.session'].sudo()

            sid = request.httprequest.session.sid
            _logger.debug('activity_logger: http request path=%s method=%s sid=%s uid=%s', request.httprequest.path, request.httprequest.method, sid, uid)
            session = ActivitySession.search([('session_key', '=', sid), ('user_id', '=', uid)], limit=1)
            if not session:
                session = ActivitySession.create({
                    'session_key': sid,
                    'user_id': uid,
                })
            req_rec = ActivityRequest.create({
                'path': request.httprequest.path,
                'root_url': request.httprequest.host_url,
                'method': request.httprequest.method,
                'user_id': uid,
                'session_id': session.id,
                'context_json': str(getattr(request, 'context', {}) or {}),
            })
            # Stash for ORM hook to link
            setattr(request, '_activity_request_id', req_rec.id)
            setattr(request, '_activity_session_id', session.id)
            _logger.debug('activity_logger: http logged request_id=%s session_id=%s', req_rec.id, session.id)
            return req_rec
        except Exception:
            _logger.exception('activity_logger: http logging failed')
            return None

    @classmethod
    def _dispatch(cls):
        # Log request before handling
        if request:
            try:
                # Use an instance-less call to helper via environment
                self = request.env['ir.http']
                self._activity_log_request()
            except Exception:
                pass
        return super()._dispatch()


