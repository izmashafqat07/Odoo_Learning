import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fbr_di_base_url = fields.Char(
        string="FBR Base URL",
        help="e.g., Sandbox/Prod gateway base URL. For Sandbox you may use your mock or PRAL sandbox.",
        default="http://localhost:5000",
    )
    fbr_di_bearer_token = fields.Char(
        string="FBR Bearer Token",
        help="Bearer token if required by gateway",
    )
    fbr_di_scenario_id = fields.Char(
        string="FBR Scenario ID",
        default="SN001",
        help="Default scenarioId to attach to payload",
    )

    # Seller defaults (if Company/Partner fields are not populated)
    fbr_di_seller_ntn_cnic = fields.Char(string="Default Seller NTN/CNIC")
    fbr_di_seller_province = fields.Char(
        string="Default Seller Province",
        default="Sindh"
    )
    fbr_di_seller_address = fields.Char(string="Default Seller Address")

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env["ir.config_parameter"].sudo()
        res.update(
            fbr_di_base_url=ICP.get_param("fbr_di.base_url", default="http://host.internal.docker:3000"),
            fbr_di_bearer_token=ICP.get_param("fbr_di.bearer_token", default=""),
            fbr_di_scenario_id=ICP.get_param("fbr_di.scenario_id", default="SN001"),
            fbr_di_seller_ntn_cnic=ICP.get_param("fbr_di.seller_ntn_cnic", default=""),
            fbr_di_seller_province=ICP.get_param("fbr_di.seller_province", default="Sindh"),
            fbr_di_seller_address=ICP.get_param("fbr_di.seller_address", default=""),
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("fbr_di.base_url", (self.fbr_di_base_url or "").strip())
        ICP.set_param("fbr_di.bearer_token", (self.fbr_di_bearer_token or "").strip())
        ICP.set_param("fbr_di.scenario_id", (self.fbr_di_scenario_id or "SN001").strip())
        ICP.set_param("fbr_di.seller_ntn_cnic", (self.fbr_di_seller_ntn_cnic or "").strip())
        ICP.set_param("fbr_di.seller_province", (self.fbr_di_seller_province or "Sindh").strip())
        ICP.set_param("fbr_di.seller_address", (self.fbr_di_seller_address or "").strip())
