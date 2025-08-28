# fbr_di_integration/models/account_move.py

import base64
import io
import json
import logging
import requests

from odoo import api, fields, models, _
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

    fbr_qr_text = fields.Text(readonly=True, copy=False)
    fbr_qr_png = fields.Binary(readonly=True, copy=False)

    # ---- Header extras ----
    fbr_invoice_type = fields.Selection([
        ("Sale Invoice", "Sale Invoice"),
        ("Credit Note", "Credit Note"),
    ], string="FBR Invoice Type", default="Sale Invoice")

    fbr_invoice_ref_no = fields.Char(string="FBR Invoice Ref No")

    # Buyer extras
    fbr_buyer_registration_type = fields.Selection([
        ("Registered", "Registered (B2B)"),
        ("Unregistered", "Unregistered (B2C)"),
    ], default="Unregistered", string="FBR Buyer Registration Type")

    # Manual tax override toggle
    fbr_use_manual_tax = fields.Boolean(string="Use FBR Manual Tax per Line")

    # ------------------- Manual tax helper -------------------
    def _get_or_create_dynamic_tax(self, rate):
        """Create/return a per-company dynamic percent tax for manual override."""
        self.ensure_one()
        company = self.company_id
        name = f"FBR Manual VAT {rate}%"
        tax = self.env['account.tax'].search([
            ('name', '=', name), ('type_tax_use', '=', 'sale'),
            ('company_id', '=', company.id),
            ('amount_type', '=', 'percent'), ('active', '=', True)
        ], limit=1)
        if tax:
            return tax
        return self.env['account.tax'].create({
            'name': name,
            'amount_type': 'percent',
            'amount': rate,
            'type_tax_use': 'sale',
            'company_id': company.id,
            'price_include': False,
        })

    def action_apply_manual_tax_rates(self):
        """Apply per-line manual tax rate to tax_ids using a dynamic tax."""
        for move in self:
            if move.move_type not in ("out_invoice", "out_refund"):
                raise UserError(_("Manual tax override allowed only on customer invoices/credit notes."))
            for line in move.invoice_line_ids.filtered(lambda l: not l.display_type):
                if move.fbr_use_manual_tax and line.fbr_manual_tax_rate is not None:
                    tax = move._get_or_create_dynamic_tax(line.fbr_manual_tax_rate)
                    line.tax_ids = [(6, 0, tax.ids)]
        return True

    # ------------------- Payload builders -------------------
    def _di_header(self):
        self.ensure_one()
        partner = self.partner_id
        company = self.company_id
        ICP = self.env['ir.config_parameter'].sudo()

        # Seller info: from company or settings fallbacks
        seller_ntn_cnic = company.vat or ICP.get_param('fbr_di.seller_ntn_cnic') or ""
        seller_name = company.name or ""
        seller_province = ICP.get_param('fbr_di.seller_province') or "Sindh"
        seller_address = company.partner_id.contact_address or ICP.get_param('fbr_di.seller_address') or ""

        # Buyer info
        buyer_ntn_cnic = self.partner_id.vat or ""
        buyer_name = partner.name or ""
        buyer_province = partner.state_id and partner.state_id.name or "Sindh"
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
            "scenarioId": ICP.get_param('fbr_di.scenario_id', default='SN001'),
        }
        return header

    def _di_items(self):
        items = []
        for line in self.invoice_line_ids.filtered(lambda l:  l.display_type == "product"):
            p = line.product_id.product_tmpl_id
            # Determine numeric sales tax rate to send
            rate = line.fbr_manual_tax_rate if (self.fbr_use_manual_tax and line.fbr_manual_tax_rate is not None) else None
            if rate is None:
                rate = (line.tax_ids[:1].amount if line.tax_ids else 0.0)

            # Product-side FBR fields (ensure you added them on product.template model)
            items.append({
                "hsCode": p.fbr_hs_code or "",
                "productDescription": line.name or p.display_name or "",
                "rate": p.fbr_rate_text or (f"{rate:.0f}%" if rate else ""),
                "uoM": p.fbr_uom_text or (line.product_uom_id and line.product_uom_id.name) or "Units",
                "quantity": float(line.quantity),
                "totalValues": 0,
                "valueSalesExcludingST": float(line.price_subtotal),
                "fixedNotifiedValueOrRetailPrice": float(p.fbr_fixed_notified_value or 0),
                "salesTaxApplicable": float(rate or 0),
                "salesTaxWithheldAtSource": 0,
                "extraTax": p.fbr_extra_tax or "",
                "furtherTax": float(p.fbr_further_tax or 0),
                "sroScheduleNo": p.fbr_sro_schedule_no or "",
                "fedPayable": 0,
                "discount": float(line.discount or 0),
                "saleType": dict(p._fields['fbr_sale_type'].selection).get(
                    p.fbr_sale_type, "Goods at standard rate (default)"
                ),
                "sroItemSerialNo": p.fbr_sro_item_serial_no or "",
            })
        return items

    def _build_di_payload(self):
        self.ensure_one()
        return {
            **self._di_header(),
            "items": self._di_items(),
        }

    # ------------------- HTTP post -------------------
    def _di_post(self, payload):
        ICP = self.env['ir.config_parameter'].sudo()
        base = (ICP.get_param('fbr_di.base_url', default='http://localhost:3000') or '').rstrip('/')
        token = (ICP.get_param('fbr_di.bearer_token', default='') or '').strip()
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
        buf = io.BytesIO(); img.save(buf, format="PNG")
        self.write({
            'fbr_qr_text': self._qr_text(),
            'fbr_qr_png': base64.b64encode(buf.getvalue()).decode('ascii'),
        })

    # ------------------- Buttons -------------------
    def action_send_to_fbr(self):
        for move in self:
            if move.state != 'posted':
                raise UserError(_("Only posted invoices can be sent to FBR."))
            if move.move_type not in ("out_invoice", "out_refund"):
                raise UserError(_("Only customer invoices / credit notes are supported."))

            payload = move._build_di_payload()
            move.write({'fbr_request_payload': json.dumps(payload, ensure_ascii=False)})

            status, body = move._di_post(payload)
            move.fbr_sent_at = fields.Datetime.now()
            move.fbr_last_response = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)

            if status == 200 and isinstance(body, dict):
                code = body.get('statusCode')
                inv_no = body.get('invoiceNumber') or body.get('InvoiceNumber')
                if code == '00' and inv_no:
                    move.write({'fbr_status': 'accepted', 'fbr_invoice_number': inv_no})
                    try:
                        move._generate_qr_png()
                    except Exception as e:
                        _logger.warning("QR generation failed: %s", e)
                        move.message_post(body=_("QR generation failed: %s") % e)
                    move.message_post(body=_("FBR accepted. Invoice Number: %s") % inv_no)
                else:
                    move.write({'fbr_status': 'rejected'})
                    move.message_post(body=_("FBR rejected: %s") % json.dumps(body))
            elif status == 401:
                move.write({'fbr_status': 'error'})
                raise UserError(_("Unauthorized by FBR (401). Check token in Settings."))
            else:
                move.write({'fbr_status': 'error'})
                raise UserError(_("FBR error (HTTP %s): %s") % (status, body))
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Per-line manual tax rate (percent)
    fbr_manual_tax_rate = fields.Float(string="FBR Manual Tax %")
