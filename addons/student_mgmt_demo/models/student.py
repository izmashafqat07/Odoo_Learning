from odoo import models, fields, api

class Student(models.Model):
    _name = 'student.mgmt'
    _description = 'Student Record'

    name = fields.Char(string='Full Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    dob = fields.Date(string='Date of Birth')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('new', 'New'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='new', string='Status')
    sequence = fields.Char(string='Sequence', readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if not vals.get('sequence'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('student.mgmt.seq')
        return super().create(vals)

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
