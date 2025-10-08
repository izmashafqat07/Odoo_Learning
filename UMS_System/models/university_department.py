from odoo import models, fields

class UniversityDepartment(models.Model):
    _name = "university.department"
    _description = "University Department"

    name = fields.Char(string="Department Name", required=True)
    code = fields.Char(string="Code")
    description = fields.Text(string="Description")
    active = fields.Boolean(default=True)
