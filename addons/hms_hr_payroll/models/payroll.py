from odoo import api, fields, models, _
from datetime import date


class HmsHrPayroll(models.Model):
    _name = "hms.hr.payroll"
    _description = "HMS Simple Payroll"
    _order = "month desc, employee_id asc"

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
        index=True,
    )

    # Month label like "August 2025" (simple, per your spec)
    month = fields.Char(
        string="Payroll Month",
        required=True,
        default=lambda self: date.today().strftime("%B %Y"),
        help="E.g., 'August 2025'",
    )

    amount = fields.Float(string="Paid Amount", required=True)

    note = fields.Text(string="Notes")

    _sql_constraints = [
        (
            "uniq_employee_month",
            "unique(employee_id, month)",
            "A payroll record already exists for this employee and month.",
        )
    ]

    def name_get(self):
        res = []
        for rec in self:
            name = f"{rec.employee_id.name} - {rec.month}"
            res.append((rec.id, name))
        return res