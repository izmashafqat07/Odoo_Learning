# fbr_mock_integration/models/res_config_settings.py
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fbr_mock_base_url = fields.Char(
        string="FBR Mock Base URL",
        help="Base URL of your mock FBR API server.",
        default="http://localhost:3000",
    )
    fbr_mock_bearer_token = fields.Char(
        string="Mock Bearer Token (optional)",
        help="Optional token used if your mock server checks Authorization header.",
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env["ir.config_parameter"].sudo()
        base = (ICP.get_param("fbr_mock.base_url", default="http://localhost:3000") or "").strip()
        token = (ICP.get_param("fbr_mock.bearer_token", default="") or "").strip()
        res.update(
            fbr_mock_base_url=base,
            fbr_mock_bearer_token=token,
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env["ir.config_parameter"].sudo()
        base = (self.fbr_mock_base_url or "http://localhost:3000").strip()
        token = (self.fbr_mock_bearer_token or "").strip()
        ICP.set_param("fbr_mock.base_url", base)
        ICP.set_param("fbr_mock.bearer_token", token)
