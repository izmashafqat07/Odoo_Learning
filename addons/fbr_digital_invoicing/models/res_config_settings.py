from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fbr_enabled = fields.Boolean("Enable FBR Integration", default=False, help="Enable auto submission to FBR.")
    fbr_block_post_on_error = fields.Boolean("Block Posting on FBR Error", default=False)

    fbr_environment = fields.Selection([("sandbox", "Sandbox"), ("production", "Production")], default="sandbox")
    fbr_client_id = fields.Char("Client ID")
    fbr_client_secret = fields.Char("Client Secret")
    fbr_api_key = fields.Char("API Key / Subscription Key")
    fbr_license_key = fields.Char("License Key")
    fbr_pos_id = fields.Char("POS ID / Device ID")
    fbr_registration_no = fields.Char("Business Registration No (NTN)")
    fbr_buyer_required = fields.Boolean("Require Buyer NTN/CNIC")
    fbr_timeout = fields.Integer("HTTP Timeout (sec)", default=30)

    fbr_auth_url_sandbox = fields.Char("Auth URL (Sandbox)", default="http://127.0.0.1:8000/auth/token")
    fbr_base_url_sandbox = fields.Char("Base API URL (Sandbox)", default="http://127.0.0.1:8000/api")

    fbr_auth_url_production = fields.Char("Auth URL (Production)")
    fbr_base_url_production = fields.Char("Base API URL (Production)")

    fbr_private_key_pem = fields.Text("Private Key (PEM)", help="RSA Private key if FBR requires signing.")
    fbr_public_key_pem = fields.Text("Public Key (PEM)")

    @api.model
    def get_values(self):
        res = super().get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        keys = [
            'fbr_enabled','fbr_block_post_on_error','fbr_environment','fbr_client_id','fbr_client_secret',
            'fbr_api_key','fbr_license_key','fbr_pos_id','fbr_registration_no','fbr_buyer_required',
            'fbr_timeout','fbr_auth_url_sandbox','fbr_base_url_sandbox','fbr_auth_url_production',
            'fbr_base_url_production','fbr_private_key_pem','fbr_public_key_pem'
        ]
        for k in keys:
            val = ICP.get_param(k, default=False)
            if val in ('True','False'):
                val = val == 'True'
            res[k] = val
        return res

    def set_values(self):
        super().set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        for field_name in [
            'fbr_enabled','fbr_block_post_on_error','fbr_environment','fbr_client_id','fbr_client_secret',
            'fbr_api_key','fbr_license_key','fbr_pos_id','fbr_registration_no','fbr_buyer_required',
            'fbr_timeout','fbr_auth_url_sandbox','fbr_base_url_sandbox','fbr_auth_url_production',
            'fbr_base_url_production','fbr_private_key_pem','fbr_public_key_pem'
        ]:
            ICP.set_param(field_name, getattr(self, field_name) or '')