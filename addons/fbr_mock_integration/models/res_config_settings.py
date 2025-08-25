from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fbr_mock_base_url = fields.Char(
        string="FBR Mock Base URL",
        help="Base URL of your mock FBR API server.",
        default="http://localhost:3000"
    )
    fbr_mock_bearer_token = fields.Char(
        string="Mock Bearer Token (optional)",
        help="Optional token used if your mock server checks Authorization header."
    )

    @api.model
    def get_values(self):
        
        res = super().get_values()
        ICP = self.env["ir.config_parameter"].sudo()
        res.update(
            fbr_mock_base_url=ICP.get_param("fbr_mock.base_url", default="http://localhost:3000"),
            fbr_mock_bearer_token=ICP.get_param("fbr_mock.bearer_token", default=""),
        )
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env["ir.config_parameter"].sudo()
        ICP.set_param("fbr_mock.base_url", self.fbr_mock_base_url or "http://localhost:3000")
        ICP.set_param("fbr_mock.bearer_token", self.fbr_mock_bearer_token or "")
