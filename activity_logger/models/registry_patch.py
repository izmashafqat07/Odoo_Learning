from odoo import models


def _inject_audit_mixin(env):
    # Attach mixin to all models dynamically where rules exist
    Rule = env['activity.rule'].sudo()
    model_names = Rule.search([('active', '=', True)]).mapped('model')
    for model_name in set(model_names):
        Model = env[model_name]._inherits and env[model_name] or env[model_name]
        # If already mixed in, skip
        if 'activity.audited.mixin' in getattr(Model, '_inherit', []) or getattr(Model, '_name', '') == 'activity.audited.mixin':
            continue
        try:
            # Inject by modifying _inherit dynamically
            inherit = list(getattr(Model, '_inherit', [])) if isinstance(getattr(Model, '_inherit', None), (list, tuple)) else [getattr(Model, '_inherit', None)] if getattr(Model, '_inherit', None) else []
            inherit.append('activity.audited.mixin')
            setattr(Model, '_inherit', tuple(x for x in inherit if x))
        except Exception:
            # Non-critical; skip problematic models
            continue


