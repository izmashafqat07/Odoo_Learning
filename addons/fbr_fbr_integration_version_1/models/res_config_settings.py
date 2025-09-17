# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # --- FBR DI (persisted via ir.config_parameter) ---
    fbr_di_base_url = fields.Char(
        string="FBR Base URL",
        help="Sandbox/Prod base URL. e.g., http://localhost:3000 or https://gw.fbr.gov.pk",
        default="http://localhost:3000",
        config_parameter="fbr_di.base_url",
    )
    fbr_di_bearer_token = fields.Char(
        string="FBR Bearer Token",
        help="Bearer token if required by gateway",
        config_parameter="fbr_di.bearer_token",
    )
    fbr_di_scenario_id = fields.Char(
        string="FBR Scenario ID",
        default="SN001",
        config_parameter="fbr_di.scenario_id",
        help="Default scenarioId to attach to payload",
    )
    fbr_di_seller_ntn_cnic = fields.Char(
        string="Default Seller NTN/CNIC",
        config_parameter="fbr_di.seller_ntn_cnic",
    )
    fbr_di_seller_province = fields.Char(
        string="Default Seller Province",
        default="Sindh",
        config_parameter="fbr_di.seller_province",
    )
    fbr_di_seller_address = fields.Char(
        string="Default Seller Address",
        config_parameter="fbr_di.seller_address",
    )

    # --- Company-related (actual values saved on res.company) ---
    # length_uom_id = fields.Many2one("uom.uom", related="company_id.length_uom_id", readonly=False)
    # area_uom_id   = fields.Many2one("uom.uom", related="company_id.area_uom_id",   readonly=False)
    # energy_uom_id = fields.Many2one("uom.uom", related="company_id.energy_uom_id", readonly=False)
    # power_uom_id  = fields.Many2one("uom.uom", related="company_id.power_uom_id",  readonly=False)
    # unit_uom_id   = fields.Many2one("uom.uom", related="company_id.unit_uom_id",   readonly=False)

    # --- Radio choices for UI (like Odoo weight/volume) ---
    # length_uom_choice = fields.Selection([("meter", "Meter"), ("foot", "Foot")], string="Length", default="meter")
    # area_uom_choice   = fields.Selection([("sqm", "Square Meter"), ("sqft", "Square Foot"), ("sqyard", "Square Yard")], string="Area", default="sqm")
    # energy_uom_choice = fields.Selection([("kwh", "Kilowatt-hour"), ("mmbtu", "MMBTU")], string="Energy", default="kwh")
    # power_uom_choice  = fields.Selection([("w", "Watt"), ("mw", "Megawatt")], string="Power", default="w")
    # unit_uom_choice   = fields.Selection([("unit", "Unit(s)"), ("dozen", "Dozen"), ("pair", "Pair"), ("thousand", "Thousand Unit"), ("set", "Set")], string="Counting Units", default="unit")

    # --------- helpers ----------
    # def _find_uom(self, names):
    #     Uom = self.env["uom.uom"]
    #     for nm in names:
    #         rec = Uom.search([("name", "=ilike", nm)], limit=1)
    #         if rec:
    #             return rec
    #     return Uom.browse(False)

    # def _map_choice_to_uom(self, kind, choice):
    #     if kind == "length":
    #         return self._find_uom(["Meter"]) if choice == "meter" else self._find_uom(["Foot", "Feet"])
    #     if kind == "area":
    #         if choice == "sqm":    return self._find_uom(["Square Meter", "Square Metre"])
    #         if choice == "sqft":   return self._find_uom(["Square Foot", "Sq Ft"])
    #         if choice == "sqyard": return self._find_uom(["Square Yard", "Sq Yard"])
    #     if kind == "energy":
    #         return self._find_uom(["Kilowatt-hour", "kWh"]) if choice == "kwh" else self._find_uom(["MMBTU"])
    #     if kind == "power":
    #         return self._find_uom(["Watt", "W"]) if choice == "w" else self._find_uom(["Megawatt", "Mega Watt", "MW"])
    #     if kind == "unit":
    #         if choice == "unit":     return self._find_uom(["Unit(s)", "Unit"])
    #         if choice == "dozen":    return self._find_uom(["Dozen"])
    #         if choice == "pair":     return self._find_uom(["Pair"])
    #         if choice == "thousand": return self._find_uom(["Thousand Unit", "Thousand Units"])
    #         if choice == "set":      return self._find_uom(["Set"])
    #     return self.env["uom.uom"].browse(False)

    # # Populate radios from company stored UoMs
    # @api.model
    # def get_values(self):
    #     res = super().get_values()
    #     company = self.env.company
    #     if company.length_uom_id:
    #         nm = company.length_uom_id.name.lower()
    #         res["length_uom_choice"] = "foot" if ("foot" in nm or "feet" in nm) else "meter"
    #     if company.area_uom_id:
    #         nm = company.area_uom_id.name.lower()
    #         res["area_uom_choice"] = "sqyard" if "yard" in nm else ("sqft" if "foot" in nm else "sqm")
    #     if company.energy_uom_id:
    #         nm = company.energy_uom_id.name.lower()
    #         res["energy_uom_choice"] = "mmbtu" if "mmbtu" in nm else "kwh"
    #     if company.power_uom_id:
    #         nm = company.power_uom_id.name.lower()
    #         res["power_uom_choice"] = "mw" if "mega" in nm else "w"
    #     if company.unit_uom_id:
    #         nm = company.unit_uom_id.name.lower()
    #         res["unit_uom_choice"] = "dozen" if "dozen" in nm else ("pair" if "pair" in nm else ("thousand" if "thousand" in nm else ("set" if "set" in nm else "unit")))
    #     return res

    # def set_values(self):
    #     super().set_values()
    #     for rec in self:
    #         if rec.length_uom_choice:
    #             rec.length_uom_id = rec._map_choice_to_uom("length", rec.length_uom_choice)
    #         if rec.area_uom_choice:
    #             rec.area_uom_id = rec._map_choice_to_uom("area", rec.area_uom_choice)
    #         if rec.energy_uom_choice:
    #             rec.energy_uom_id = rec._map_choice_to_uom("energy", rec.energy_uom_choice)
    #         if rec.power_uom_choice:
    #             rec.power_uom_id = rec._map_choice_to_uom("power", rec.power_uom_choice)
    #         if rec.unit_uom_choice:
    #             rec.unit_uom_id = rec._map_choice_to_uom("unit", rec.unit_uom_choice)

    # # Instant reflect on UI
    # @api.onchange("length_uom_choice")
    # def _onchange_length(self):
    #     self.length_uom_id = self._map_choice_to_uom("length", self.length_uom_choice)

    # @api.onchange("area_uom_choice")
    # def _onchange_area(self):
    #     self.area_uom_id = self._map_choice_to_uom("area", self.area_uom_choice)

    # @api.onchange("energy_uom_choice")
    # def _onchange_energy(self):
    #     self.energy_uom_id = self._map_choice_to_uom("energy", self.energy_uom_choice)

    # @api.onchange("power_uom_choice")
    # def _onchange_power(self):
    #     self.power_uom_id = self._map_choice_to_uom("power", self.power_uom_choice)

    # @api.onchange("unit_uom_choice")
    # def _onchange_unit(self):
    #     self.unit_uom_id = self._map_choice_to_uom("unit", self.unit_uom_choice)
