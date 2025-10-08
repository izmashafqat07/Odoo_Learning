from odoo import api, fields, models


class ActivityRule(models.Model):
    _name = 'activity.rule'
    _description = 'Activity Tracking Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    model_id = fields.Many2one('ir.model', required=True, ondelete='cascade')
    model = fields.Char(related='model_id.model', store=True)
    track_create = fields.Boolean(default=True)
    track_write = fields.Boolean(default=True)
    track_unlink = fields.Boolean(default=True)
    track_read = fields.Boolean(default=False)
    track_export = fields.Boolean(default=False)
    mode = fields.Selection([('quick', 'Quick'), ('detailed', 'Detailed')], default='detailed', required=True)
    excluded_user_ids = fields.Many2many('res.users', string='Excluded Users')
    excluded_field_ids = fields.Many2many('ir.model.fields', string='Excluded Fields', domain="[('model_id','=',model_id)]")

    def applies_to(self, model_name, method, user_id):
        self.ensure_one()
        if not self.active:
            return False
        if self.model_id.model != model_name:
            return False
        if user_id in self.excluded_user_ids.ids:
            return False
        method_flag = {
            'create': self.track_create,
            'write': self.track_write,
            'unlink': self.track_unlink,
            'read': self.track_read,
            'export': self.track_export,
        }.get(method, False)
        return bool(method_flag)


