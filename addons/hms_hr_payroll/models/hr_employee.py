from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Link employee to HMS Department
    hms_department_id = fields.Many2one(
        comodel_name="hms.base.department",
        string="HMS Department",
        help="Hospital department for this employee.",
    )

    # Lightweight salary for basic payroll usage
    hms_salary = fields.Float(
        string="Monthly Salary",
        help="Simple monthly salary field for basic payroll tracking.",
    )

    # Reverse link to Doctor profile if any
    hms_doctor_ids = fields.One2many(
        comodel_name="hms.base.doctor",
        inverse_name="employee_id",
        string="Related Doctors",
        readonly=True,
    )

    hms_doctor_count = fields.Integer(
        string="Doctors",
        compute="_compute_hms_doctor_count",
        readonly=True,
    )

    @api.depends("hms_doctor_ids")
    def _compute_hms_doctor_count(self):
        for rec in self:
            rec.hms_doctor_count = len(rec.hms_doctor_ids)

    def action_open_related_doctors(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("hms_base.action_hms_doctor")
        # If the base action id is different in your module, adjust the XML ID above.
        action.update({
            "domain": [("employee_id", "=", self.id)],
            "context": {"default_employee_id": self.id},
        })
        return action