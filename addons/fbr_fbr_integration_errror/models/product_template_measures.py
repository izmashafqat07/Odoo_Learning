# -*- coding: utf-8 -*-
from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_length_value = fields.Float(string="Length")
    x_area_value   = fields.Float(string="Area")
    x_energy_value = fields.Float(string="Energy")
    x_power_value  = fields.Float(string="Power")

    x_length_uom_id = fields.Many2one(
        "uom.uom", string="Length UoM",
        default=lambda self: self.env.company.length_uom_id.id or False,
        domain="[('category_id.name','=','Length')]",
    )
    x_area_uom_id = fields.Many2one(
        "uom.uom", string="Area UoM",
        default=lambda self: self.env.company.area_uom_id.id or False,
        domain="[('category_id.name','=','Area')]",
    )
    x_energy_uom_id = fields.Many2one(
        "uom.uom", string="Energy UoM",
        default=lambda self: self.env.company.energy_uom_id.id or False,
        domain="[('category_id.name','=','Energy')]",
    )
    x_power_uom_id = fields.Many2one(
        "uom.uom", string="Power UoM",
        default=lambda self: self.env.company.power_uom_id.id or False,
        domain="[('category_id.name','=','Power')]",
    )

    x_unit_uom_id = fields.Many2one(
        "uom.uom", string="Counting UoM",
        default=lambda self: self.env.company.unit_uom_id.id or False,
        domain="[('category_id.name','=','Unit')]",
        help="e.g., Unit(s), Dozen, Pair, Thousand Unit, Set",
    )