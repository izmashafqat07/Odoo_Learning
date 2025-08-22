import requests
import time
import json
from datetime import datetime, timedelta
from odoo import api, models, _
from odoo.exceptions import UserError
from .qr_utils import make_qr_bytes

class FBRClient(models.AbstractModel):
    _name = "fbr.client"
    _description = "FBR API Client"

    _token_cache = {}

    def _get_env_key(self):
        ICP = self.env['ir.config_parameter'].sudo()
        env = ICP.get_param('fbr_environment') or 'sandbox'
        return 'production' if env == 'production' else 'sandbox'

    def _get_base_urls(self):
        ICP = self.env['ir.config_parameter'].sudo()
        env = self._get_env_key()
        if env == 'production':
            return {
                "auth": ICP.get_param('fbr_auth_url_production') or "",
                "base": ICP.get_param('fbr_base_url_production') or "",
            }
        else:
            return {
                "auth": ICP.get_param('fbr_auth_url_sandbox') or "http://127.0.0.1:8000/auth/token",
                "base": ICP.get_param('fbr_base_url_sandbox') or "http://127.0.0.1:8000/api",
            }

    def _get_credentials(self):
        ICP = self.env['ir.config_parameter'].sudo()
        return {
            "client_id": ICP.get_param('fbr_client_id') or "",
            "client_secret": ICP.get_param('fbr_client_secret') or "",
            "api_key": ICP.get_param('fbr_api_key') or "",
            "license_key": ICP.get_param('fbr_license_key') or "",
            "pos_id": ICP.get_param('fbr_pos_id') or "",
            "registration_no": ICP.get_param('fbr_registration_no') or "",
            "timeout": int(ICP.get_param('fbr_timeout') or 30)
        }

    def _get_token(self):
        urls = self._get_base_urls()
        creds = self._get_credentials()
        cache_key = (urls['auth'], creds['client_id'])
        token_entry = self._token_cache.get(cache_key)
        if token_entry and token_entry['expires_at'] > time.time():
            return token_entry['access_token']

        payload = {
            "client_id": creds['client_id'],
            "client_secret": creds['client_secret'],
            "grant_type": "client_credentials"
        }
        headers = {"Content-Type": "application/json", "x-api-key": creds['api_key']}
        timeout = creds['timeout']
        resp = requests.post(urls['auth'], data=json.dumps(payload), headers=headers, timeout=timeout)
        if resp.status_code >= 400:
            raise UserError(_("FBR auth failed: %s") % resp.text)
        data = resp.json()
        access_token = data.get("access_token") or data.get("token")
        expires_in = int(data.get("expires_in") or 1800)
        self._token_cache[cache_key] = {
            "access_token": access_token,
            "expires_at": time.time() + expires_in - 30,
        }
        return access_token

    def _headers(self):
        token = self._get_token()
        creds = self._get_credentials()
        return {
            "Authorization": f"Bearer {token}",
            "x-api-key": creds['api_key'],
            "x-license-key": creds['license_key'],
            "Content-Type": "application/json",
        }

    # -------- Public helpers ----------
    def make_qr_image(self, data: str) -> bytes:
        return make_qr_bytes(data)

    # -------- API calls ----------
    def submit_invoice(self, payload: dict) -> dict:
        urls = self._get_base_urls()
        endpoint = urls['base'].rstrip('/') + "/invoices"
        headers = self._headers()
        creds = self._get_credentials()
        payload = dict(payload)
        payload.setdefault("POSID", creds['pos_id'])
        payload.setdefault("SellerNTN", creds['registration_no'])

        resp = requests.post(endpoint, data=json.dumps(payload), headers=headers, timeout=creds['timeout'])
        if resp.status_code >= 400:
            return {"success": False, "message": resp.text}
        data = resp.json()
        return data

    def cancel_invoice(self, payload: dict) -> dict:
        urls = self._get_base_urls()
        endpoint = urls['base'].rstrip('/') + "/invoices/cancel"
        headers = self._headers()
        creds = self._get_credentials()
        resp = requests.post(endpoint, data=json.dumps(payload), headers=headers, timeout=creds['timeout'])
        if resp.status_code >= 400:
            return {"success": False, "message": resp.text}
        return resp.json()