# fbr_fbr_integration/models/account_move.py
# -*- coding: utf-8 -*-

import base64
import io
import json
import logging

import requests
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Optional QR dependency
try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_M
    _FBR_QR = True
except Exception:
    _FBR_QR = False


class AccountMove(models.Model):
    _inherit = "account.move"

    # ---- Status & artifacts ----
    fbr_status = fields.Selection(
        [
            ("not_sent", "Not Sent"),
            ("sent", "Sent"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("error", "Error"),
        ],
        default="not_sent",
        copy=False,
        readonly=True,
    )
    fbr_invoice_number = fields.Char(readonly=True, copy=False)
    fbr_last_response = fields.Text(readonly=True, copy=False)
    fbr_sent_at = fields.Datetime(readonly=True, copy=False)
    fbr_request_payload = fields.Text(readonly=True, copy=False)
    fbr_qr_text = fields.Text(readonly=True, copy=False)
    fbr_qr_png = fields.Binary(readonly=True, copy=False)

    # ---- Header extras ----
    fbr_invoice_type = fields.Selection(
        [("Sale Invoice", "Sale Invoice"), ("Credit Note", "Credit Note")],
        string="FBR Invoice Type",
        default="Sale Invoice",
    )
    fbr_invoice_ref_no = fields.Char(string="FBR Invoice Ref No")

    # Buyer extras
    fbr_buyer_registration_type = fields.Selection(
        [("Registered", "Registered (B2B)"), ("Unregistered", "Unregistered (B2C)")],
        default="Unregistered",
        string="FBR Buyer Registration Type",
    )
    
    

    # ------------------- Payload builders -------------------
    def _di_header(self):
        self.ensure_one()
        partner = self.partner_id
        company = self.company_id
        ICP = self.env["ir.config_parameter"].sudo()

        # Seller info
        seller_ntn_cnic = company.vat or ICP.get_param("fbr_di.seller_ntn_cnic") or ""
        seller_name = company.name or ""
        seller_province = ICP.get_param("fbr_di.seller_province") or "Sindh"
        seller_address = (
            company.partner_id.contact_address
            or ICP.get_param("fbr_di.seller_address")
            or ""
        )

        # Buyer info
        buyer_ntn_cnic = partner.vat or ""
        buyer_name = partner.name or ""
        buyer_province = partner.state_id.name if partner.state_id else "Sindh"
        buyer_address = partner.contact_address or (partner.street or "")

        header = {
            "invoiceType": self.fbr_invoice_type or "Sale Invoice",
            "invoiceDate": str(self.invoice_date or fields.Date.context_today(self)),
            "sellerNTNCNIC": seller_ntn_cnic,
            "sellerBusinessName": seller_name,
            "sellerProvince": seller_province,
            "sellerAddress": seller_address,
            "buyerNTNCNIC": buyer_ntn_cnic,
            "buyerBusinessName": buyer_name,
            "buyerProvince": buyer_province,
            "buyerAddress": buyer_address,
            "buyerRegistrationType": self.fbr_buyer_registration_type or "Unregistered",
            "invoiceRefNo": self.fbr_invoice_ref_no or (self.name or f"INV-{self.id}"),
            "scenarioId": ICP.get_param("fbr_di.scenario_id", default="SN001"),
        }
        return header

    def _di_items(self):
        """
        Build DI items[] from invoice lines using:
        - ONLY real product lines: display_type is False
        - UoM from PRODUCT General Information: product.template.uom_id
          (yehi UoM Sales/Cost ke sath 'per <UoM>' me dikh rahi hoti hai)
        - HS Code from PRODUCT Inventory tab (standard 'hs_code'; fallback common custom names)
        - totalValues = line.price_total (incl. tax)
        - valueSalesExcludingST = line.price_subtotal (excl. tax)
        """
        items = []
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'):
            p = line.product_id.product_tmpl_id if line.product_id else False

            # ---- Tax rate: numeric + display text ----
            rate_num = line.tax_ids[:1].amount if line.tax_ids else 0.0
            if p and getattr(p, "fbr_rate_text", False):
                rate_txt = p.fbr_rate_text
            else:
                rate_txt = f"{rate_num:.0f}%" if rate_num else ""

            # ---- UoM from PRODUCT General Information (selling UoM) ----
            uom_rec = (p and p.uom_id) or line.product_uom_id
            uom_name = (uom_rec and uom_rec.name) or "Unit(s)"
            uom_code = (uom_rec and getattr(uom_rec, "fbr_code", "")) or ""

            # ---- HS Code from PRODUCT Inventory tab ----
            inv_hs = ""
            if p:
                inv_hs = (
                    getattr(p, "hs_code", False)
                    or getattr(p, "x_hs_code", False)
                    or getattr(p, "l10n_pk_hs_code", False)
                    or ""
                )

            items.append(
                {
                    "hsCode": inv_hs,  # Inventory HS Code (NOT custom fbr_hs_code)
                    "productDescription": (line.name or (p and p.display_name) or "")[:512],
                    "rate": rate_txt,     # text per DI spec
                    "uoM": uom_name,      # General Info UoM name (per ...)
                    "uomCode": uom_code,  # FBR UoM code from uom.uom.fbr_code
                    "quantity": float(line.quantity or 0.0),

                    # tax-inclusive total per line:
                    "totalValues": float(line.price_total or 0.0),

                    # excl.-tax subtotal per line:
                    "valueSalesExcludingST": float(line.price_subtotal or 0.0),

                    # Optional DI extras from product fields
                    "fixedNotifiedValueOrRetailPrice": float(
                        (p and getattr(p, "fbr_fixed_notified_value", 0.0)) or 0.0
                    ),
                    "salesTaxApplicable": float(rate_num or 0.0),
                    "salesTaxWithheldAtSource": 0,
                    "extraTax": (p and getattr(p, "fbr_extra_tax", "") or ""),
                    "furtherTax": float((p and getattr(p, "fbr_further_tax", 0.0)) or 0.0),
                    "sroScheduleNo": (p and getattr(p, "fbr_sro_schedule_no", "") or ""),
                    "fedPayable": 0,
                    "discount": float(line.discount or 0.0),
                    "saleType": (
                        dict(p._fields["fbr_sale_type"].selection).get(
                            getattr(p, "fbr_sale_type", False),
                            "Goods at standard rate (default)",
                        )
                        if (p and hasattr(p, "fbr_sale_type"))
                        else "Goods at standard rate (default)"
                    ),
                    "sroItemSerialNo": (p and getattr(p, "fbr_sro_item_serial_no", "") or ""),
                }
            )
        return items

    def _build_di_payload(self):
        self.ensure_one()
        return {
            **self._di_header(),
            "items": self._di_items(),
        }

    # ------------------- HTTP post -------------------
    def _di_post(self, payload):
        ICP = self.env["ir.config_parameter"].sudo()
        base = (ICP.get_param("fbr_di.base_url", default="http://localhost:3000") or "").rstrip("/")
        token = (ICP.get_param("fbr_di.bearer_token", default="") or "").strip()
        url = f"{base}/di_data/v1/di/postinvoicedata"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=45)
        except requests.RequestException as e:
            raise UserError(_("Network error while contacting FBR: %s") % e)
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        return resp.status_code, body

    # ------------------- QR helpers -------------------
    def _qr_text(self):
        self.ensure_one()
        return (self.fbr_invoice_number or self.name or "").strip()

    def _generate_qr_png(self):
        self.ensure_one()
        if not _FBR_QR:
            raise UserError(_("Install 'qrcode[pil]' to generate QR codes"))
        qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M, box_size=6, border=2)
        qr.add_data(self._qr_text())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        self.write(
            {
                "fbr_qr_text": self._qr_text(),
                "fbr_qr_png": base64.b64encode(buf.getvalue()).decode("ascii"),
            }
        )

    # ------------------- Buttons -------------------
    def action_send_to_fbr(self):
        for move in self:
            if move.state != "posted":
                raise UserError(_("Only posted invoices can be sent to FBR."))
            if move.move_type not in ("out_invoice", "out_refund"):
                raise UserError(_("Only customer invoices / credit notes are supported."))

            payload = move._build_di_payload()
            move.write({"fbr_request_payload": json.dumps(payload, ensure_ascii=False)})

            status, body = self._di_post(payload)
            move.fbr_sent_at = fields.Datetime.now()
            move.fbr_last_response = body if isinstance(body, str) else json.dumps(
                body, ensure_ascii=False
            )

            if status == 200 and isinstance(body, dict):
                code = body.get("statusCode")
                inv_no = body.get("invoiceNumber") or body.get("InvoiceNumber")
                if code == "00" and inv_no:
                    move.write({"fbr_status": "accepted", "fbr_invoice_number": inv_no})
                    try:
                        move._generate_qr_png()
                    except Exception as e:
                        _logger.warning("QR generation failed: %s", e)
                        move.message_post(body=_("QR generation failed: %s") % e)
                    move.message_post(body=_("FBR accepted. Invoice Number: %s") % inv_no)
                else:
                    move.write({"fbr_status": "rejected"})
                    move.message_post(body=_("FBR rejected: %s") % json.dumps(body))
            elif status == 401:
                move.write({"fbr_status": "error"})
                raise UserError(_("Unauthorized by FBR (401). Check token in Settings."))
            else:
                move.write({"fbr_status": "error"})
                raise UserError(_("FBR error (HTTP %s): %s") % (status, body))
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    # (no per-line custom tax fields)
