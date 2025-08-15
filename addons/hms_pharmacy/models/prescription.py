from odoo import fields, models

class HmsPrescription(models.Model):
    _name = 'hms.prescription'
    _description = 'Patient Prescription'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Prescription Ref',
        required=True,
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code('hms.prescription') or '/'
    )
    patient_id = fields.Many2one('hms.base.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('hms.base.doctor', string='Doctor')
    medicine_ids = fields.Many2many(
        'product.product',
        string='Medicines',
        domain=[('is_medicine', '=', True)]
    )
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    note = fields.Text(string='Notes')
