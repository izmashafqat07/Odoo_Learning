from odoo import api, fields, models, _


class HmsBaseDoctor(models.Model):
    _inherit = "hms.base.doctor"

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        help="HR employee record for this doctor.",
    )

    def action_create_employee(self):
        """Create an hr.employee from this doctor and link it."""
        for doctor in self:
            if doctor.employee_id:
                # Already linked
                continue
            vals = {
                "name": doctor.name or _("New Employee"),
                "hms_department_id": doctor.department_id.id,
            }
            employee = self.env["hr.employee"].create(vals)
            doctor.employee_id = employee.id
        # Open the newly linked employee if single
        if len(self) == 1 and self.employee_id:
            action = self.env["ir.actions.actions"]._for_xml_id("hr.open_view_employee_list_my")
            action.update({
                "domain": [("id", "=", self.employee_id.id)],
                "views": [(False, "form")],
                "res_id": self.employee_id.id,
            })
            return action
        return True