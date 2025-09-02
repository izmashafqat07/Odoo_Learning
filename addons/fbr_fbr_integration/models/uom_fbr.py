# -*- coding: utf-8 -*-
from odoo import fields, models

class Uom(models.Model):
    _inherit = 'uom.uom'

    fbr_code = fields.Char(
        string='FBR Code', 
        help='FBR code for tax compliance in Pakistan'
        )