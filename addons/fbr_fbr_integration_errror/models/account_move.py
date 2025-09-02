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


# =========================
# Account Move (Invoice)
# =========================
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

    # ---- FBR totals (computed for display)
    amount_extra_tax = fields.Monetary(currency_field='currency_id', compute='_compute_fbr_amounts', store=False)
    amount_further_tax = fields.Monetary(currency_field='currency_id', compute='_compute_fbr_amounts', store=False)
    amount_total_with_all = fields.Monetary(currency_field='currency_id', compute='_compute_fbr_amounts', store=False)

    @api.depends('invoice_line_ids.price_total',
                 'invoice_line_ids.fbr_extra_tax_amount',
                 'invoice_line_ids.fbr_further_tax_amount')
    def _compute_fbr_amounts(self):
        for move in self:
            extra = sum(move.invoice_line_ids.mapped('fbr_extra_tax_amount') or [])
            further = sum(move.invoice_line_ids.mapped('fbr_further_tax_amount') or [])
            move.amount_extra_tax = extra
            move.amount_further_tax = further
            move.amount_total_with_all = (move.amount_total or 0.0) + extra + further

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
        seller_address = company.partner_id.contact_address or ICP.get_param("fbr_di.seller_address") or ""

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
        """Build DI items[] from invoice lines.

        - Use real product lines only (display_type is False)
        - totalValues = line.price_total (incl. tax)
        - valueSalesExcludingST = line.price_subtotal (excl. tax)
        - Tax rate derived from first tax on line (if any)
        """
        items = []
        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            p = line.product_id.product_tmpl_id

            # Determine numeric sales tax rate to send (from line taxes only)
            rate = line.tax_ids[:1].amount if line.tax_ids else 0.0

            # Prefer FBR UOM code if available, else product text, else UoM name, else Unit(s)
            uom_code = getattr(line.product_uom_id, "fbr_code", False) or ""
            uom_text = (
                uom_code
                or getattr(p, "fbr_uom_text", False)
                or (line.product_uom_id and line.product_uom_id.name)
                or "Unit(s)"
            )

            # Product-level attributes (if your product module defines them)
            extra_tax_text = getattr(p, "fbr_extra_tax", "") or ""
            further_tax_rate = float(getattr(p, "fbr_further_tax", 0.0) or 0.0)

            items.append(
                {
                    "hsCode": getattr(p, "fbr_hs_code", "") or "",
                    "productDescription": line.name or p.display_name or "",
                    "rate": getattr(p, "fbr_rate_text", "") or (f"{rate:.0f}%" if rate else ""),
                    "uoM": uom_text,
                    "quantity": float(line.quantity or 0.0),
                    "totalValues": float(line.price_total or 0.0),            # incl. tax
                    "valueSalesExcludingST": float(line.price_subtotal or 0.0),# excl. tax
                    "fixedNotifiedValueOrRetailPrice": float(
                        getattr(p, "fbr_fixed_notified_value", 0.0) or 0.0
                    ),
                    "salesTaxApplicable": float(rate or 0.0),
                    "salesTaxWithheldAtSource": 0,
                    "extraTax": extra_tax_text,
                    "furtherTax": further_tax_rate,
                    "sroScheduleNo": getattr(p, "fbr_sro_schedule_no", "") or "",
                    "fedPayable": 0,
                    "discount": float(line.discount or 0.0),
                    "saleType": (
                        dict(p._fields["fbr_sale_type"].selection).get(
                            getattr(p, "fbr_sale_type", False),
                            "Goods at standard rate (default)",
                        )
                        if hasattr(p, "fbr_sale_type")
                        else "Goods at standard rate (default)"
                    ),
                    "sroItemSerialNo": getattr(p, "fbr_sro_item_serial_no", "") or "",
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

            status, body = move._di_post(payload)
            move.fbr_sent_at = fields.Datetime.now()
            move.fbr_last_response = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)

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


# =========================
# Account Move Line (Invoice line)
# =========================
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Computed amounts for display in the tree
    fbr_extra_tax_amount = fields.Monetary(
        currency_field='currency_id', compute='_compute_fbr_line_amounts', store=False
    )
    fbr_further_tax_amount = fields.Monetary(
        currency_field='currency_id', compute='_compute_fbr_line_amounts', store=False
    )
    fbr_line_total_incl_all = fields.Monetary(
        currency_field='currency_id', compute='_compute_fbr_line_amounts', store=False
    )

    @api.depends('price_total', 'price_subtotal', 'product_id', 'discount', 'quantity', 'tax_ids')
    def _compute_fbr_line_amounts(self):
        """
        Heuristic demo:
        - If product template defines `fbr_extra_tax_rate` (percent) and/or `fbr_further_tax` (percent),
          compute amounts from line price_subtotal.
        - Otherwise, default to 0.0 to avoid errors.
        """
        for line in self:
            base = float(line.price_subtotal or 0.0)
            p = line.product_id.product_tmpl_id

            # Percent rates (0..100). If not present on product, assume zero.
            extra_rate = 0.0
            if hasattr(p, 'fbr_extra_tax_rate'):
                try:
                    extra_rate = float(getattr(p, 'fbr_extra_tax_rate') or 0.0)
                except Exception:
                    extra_rate = 0.0

            further_rate = 0.0
            if hasattr(p, 'fbr_further_tax'):
                try:
                    further_rate = float(getattr(p, 'fbr_further_tax') or 0.0)
                except Exception:
                    further_rate = 0.0

            extra_amt = base * extra_rate / 100.0
            further_amt = base * further_rate / 100.0

            line.fbr_extra_tax_amount = extra_amt
            line.fbr_further_tax_amount = further_amt
            line.fbr_line_total_incl_all = float(line.price_total or 0.0) + extra_amt + further_amt
