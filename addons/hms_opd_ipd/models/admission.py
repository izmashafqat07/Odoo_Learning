from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HmsAdmission(models.Model):
    _name = 'hms.admission'
    _description = 'Patient Admission'
    _order = 'admission_date desc'

    patient_id = fields.Many2one(
        'hms.base.patient',
        string='Patient',
        required=True,
        ondelete='cascade'
    )
    doctor_id = fields.Many2one(
        'hms.base.doctor',
        string='Doctor',
        required=True
    )
    admission_type = fields.Selection(
        [('opd', 'OPD'), ('ipd', 'IPD')],
        string='Type',
        required=True
    )
    admission_date = fields.Datetime(
        default=fields.Datetime.now,
        required=True
    )
    discharge_date = fields.Datetime()
    bed_no = fields.Char(string='Bed No.', help="Applicable only for IPD")
    notes = fields.Text()
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('admitted', 'Admitted'),
            ('discharged', 'Discharged'),
            ('canceled', 'Canceled')
        ],
        default='draft',
        tracking=True
    )

    @api.onchange('admission_type')
    def _onchange_admission_type(self):
        """Set default values depending on OPD/IPD"""
        if self.admission_type == 'opd':
            self.bed_no = False
            self.notes = self.notes or "Consultation Visit"
        elif self.admission_type == 'ipd':
            self.notes = self.notes or "Inpatient Admission - assign bed"
            if not self.bed_no:
                self.bed_no = f"Bed-{fields.Datetime.now().strftime('%H%M%S')}"

    @api.constrains('discharge_date', 'admission_date')
    def _check_dates(self):
        for rec in self:
            if rec.discharge_date and rec.discharge_date < rec.admission_date:
                raise ValidationError("Discharge date cannot be before admission date.")

    def action_admit(self):
        self.state = 'admitted'

    def action_discharge(self):
        self.write({
            'state': 'discharged',
            'discharge_date': fields.Datetime.now()
        })

    def action_cancel(self):
        self.state = 'canceled'

    def action_reset_to_draft(self):
        self.state = 'draft'
