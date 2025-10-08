from odoo import models, fields, api

class UniversityUserType(models.Model):
    _name = "university.user.type"
    _description = "University User Type"

    name = fields.Char(required=True)
    group_ids = fields.Many2many("res.groups", string="Associated Groups")
