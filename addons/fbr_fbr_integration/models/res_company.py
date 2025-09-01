# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    length_uom_id = fields.Many2one("uom.uom", string="Default Length UoM")
    area_uom_id   = fields.Many2one("uom.uom", string="Default Area UoM")
    energy_uom_id = fields.Many2one("uom.uom", string="Default Energy UoM")
    power_uom_id  = fields.Many2one("uom.uom", string="Default Power UoM")
    unit_uom_id   = fields.Many2one("uom.uom", string="Default Counting UoM")
