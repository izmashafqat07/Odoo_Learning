# -*- coding: utf-8 -*-
from odoo import fields, models

class UomUom(models.Model):
    _inherit = "uom.uom"

    fbr_code = fields.Char(string="FBR UOM Code", index=True)
    _sql_constraints = [
        ('fbr_code_unique', 'unique(fbr_code)', 'FBR UOM Code must be unique.')
    ]
