# fbr_mock_integration/models/account_move.py

import base64
import io
import json
import logging
import requests  # HTTP calls

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Optional dependency for QR
try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_M
    _FBR_QR_AVAILABLE = True
except Exception:
    _FBR_QR_AVAILABLE = False


class AccountMove(models.Model):
    _inherit = "account.move"

    # -------------------------------
    # FBR tracking fields
    # -------------------------------
    fbr_status = fields.Selection([
        ("not_sent", "Not Sent"),
        ("sent", "Sent"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("error", "Error"),
    ], default="not_sent", copy=False, readonly=True)

    fbr_invoice_number = fields.Char(readonly=True, copy=False)
    fbr_last_response = fields.Text(readonly=True, copy=False)
    fbr_sent_at = fields.Datetime(readonly=True, copy=False)
    fbr_request_payload = fields.Text(readonly=True, copy=False)

    # QR for report (shown on PDF)
    fbr_qr_text = fields.Text(readonly=True, copy=False, help="Raw text encoded in QR")
    fbr_qr_png = fields.Binary(readonly=True, copy=False, help="PNG image for printing (1x1 inch on report)")

    # -------------------------------
    # Payload to Mock FBR
    # -------------------------------
    def _build_fbr_mock_payload(self):
        """
        Build a simple JSON payload compatible with your mock server.
        Adjust keys to real DI spec when you move from mock -> prod.
        """
        self.ensure_one()
        if self.move_type not in ("out_invoice", "out_refund"):
            raise UserError(_("Only customer invoices/credit notes can be sent."))

        partner = self.partner_id
        company = self.company_id

        header = {
            "invoiceNumberLocal": self.name or f"INV-{self.id}",
            "invoiceDate": fields.Datetime.to_string(
                self.invoice_date or fields.Date.context_today(self)
            ),
            "sellerName": company.name or "",
            "sellerNTN": company.vat or "",  # optional
            "buyerName": partner.name or "",
            "buyerNTN": partner.vat or "",   # optional
            "totalExclTax": float(self.amount_untaxed),
            "totalTax": float(self.amount_tax),
            "totalInclTax": float(self.amount_total),
            "currency": self.currency_id.name or "PKR",
        }

        items = []
        line_no = 1
        # Only real invoice lines (skip sections/notes)
        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            tax_amount = float(line.price_total - line.price_subtotal)
            items.append({
                "lineNo": line_no,
                "description": line.name or (line.product_id.display_name or "Item"),
                # TODO: map actual HS code field later; barcode used as placeholder
                "hsCode": getattr(line.product_id, "barcode", "") or "",
                "qty": float(line.quantity),
                "uom": (line.product_uom_id and line.product_uom_id.name) or "Units",
                "unitPrice": float(line.price_unit),
                # NOTE: price_subtotal is net (excl. tax); mock key named 'grossAmount' originally.
                # Keep as-is for mock compatibility; rename when moving to prod DI schema.
                "grossAmount": float(line.price_subtotal),
                "taxAmount": tax_amount,
            })
            line_no += 1

        payload = {
            "invoiceHeader": header,
            "invoiceItems": items,
        }
        return payload

    # -------------------------------
    # HTTP POST to mock
    # -------------------------------
    def _fbr_mock_post(self, endpoint="/di_data/v1/di/postinvoicedata", payload=None):
        """
        POST to mock server; returns (status_code, json_dict or text).
        Reads base URL + token from ir.config_parameter:
          - fbr_mock.base_url (default http://localhost:3000)
          - fbr_mock.bearer_token
        """
        ICP = self.env["ir.config_parameter"].sudo()
        base = ICP.get_param("fbr_mock.base_url", default="http://localhost:3000").rstrip("/")
        token = ICP.get_param("fbr_mock.bearer_token", default="").strip()

        url = f"{base}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        _logger.info("Sending invoice to FBR mock: %s", url)
        _logger.debug("Payload: %s", json.dumps(payload, indent=2, ensure_ascii=False))

        # Network call with clear error surfacing
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
        except requests.RequestException as e:
            raise UserError(_("Network error while contacting FBR mock: %s") % e)

        try:
            body = resp.json()
        except ValueError:
            body = resp.text

        return resp.status_code, body

    # -------------------------------
    # QR helpers (encode ONLY FBR number)
    # -------------------------------
    def _build_fbr_qr_text(self):
        """
        Return ONLY the FBR invoice number as QR content
        (per your Asaan Tax auto-fill requirement).
        """
        self.ensure_one()
        inv_no = (self.fbr_invoice_number or "").strip()
        # Optional fallback: if not available (edge), use local name
        if not inv_no:
            inv_no = (self.name or "").strip()
        return inv_no

    def _generate_fbr_qr_png(self):
        """
        Generate QR PNG; auto-size to fit content and store in fbr_qr_png.
        """
        self.ensure_one()
        if not _FBR_QR_AVAILABLE:
            raise UserError(_(
                "Python 'qrcode' or 'Pillow' not installed. "
                "Please install: pip install qrcode[pil]"
            ))

        text = self._build_fbr_qr_text()

        # Auto-size to prevent overflow for any data length
        qr = qrcode.QRCode(
            version=None,                  # auto
            error_correction=ERROR_CORRECT_M,
            box_size=6,                    # report scales to ~1 inch
            border=2
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        # Store base64 as string to be safe for QWeb rendering
        png_str = base64.b64encode(buf.getvalue()).decode("ascii")
        self.write({"fbr_qr_text": text, "fbr_qr_png": png_str})

    # -------------------------------
    # Button: Send to FBR (Mock)
    # -------------------------------
    def action_send_to_fbr_mock(self):
        """
        Manual button to send a posted invoice to your local mock server.
        On success (statusCode '00'): save fbr_invoice_number and generate QR.
        """
        for move in self:
            if move.state != "posted":
                raise UserError(_("Only posted invoices can be sent to FBR."))

            payload = move._build_fbr_mock_payload()
            move.write({
                "fbr_request_payload": json.dumps(payload, ensure_ascii=False),
            })

            status, body = move._fbr_mock_post(payload=payload)

            # Save raw response for debugging
            move.fbr_last_response = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
            # Even on failure we log the attempt time
            move.fbr_sent_at = fields.Datetime.now()

            # Expected mock success:
            # {
            #   "invoiceNumber": "FBR-TEST-INV-001",
            #   "statusCode": "00",
            #   "status": "Valid",
            #   "errorCode": null,
            #   "exception": null
            # }
            if status == 200 and isinstance(body, dict):
                status_code = body.get("statusCode")
                inv_no = body.get("invoiceNumber")
                if status_code == "00":
                    move.write({
                        "fbr_status": "accepted",
                        "fbr_invoice_number": inv_no or "",
                    })
                    # Build QR on acceptance; never crash the button if QR deps missing
                    try:
                        move._generate_fbr_qr_png()
                    except Exception as e:
                        _logger.warning("QR generation failed: %s", e)
                        move.message_post(body=_("QR generation failed: %s") % e)

                    move.message_post(body=_("FBR Mock accepted. Invoice Number: %s") % (inv_no or "N/A"))
                else:
                    move.write({"fbr_status": "rejected"})
                    move.message_post(body=_("FBR Mock rejected: %s") % json.dumps(body))

            elif status == 401:
                move.write({"fbr_status": "error"})
                raise UserError(_("Unauthorized by FBR mock (401). Check token in Settings."))
            else:
                move.write({"fbr_status": "error"})
                raise UserError(_("FBR mock error (HTTP %s): %s") % (status, body))

        return True
