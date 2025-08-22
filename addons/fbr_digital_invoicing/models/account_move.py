import base64
import json
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    fbr_state = fields.Selection([
        ('not_submitted', 'Not Submitted'),
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], string="FBR Status", default='not_submitted', tracking=True, copy=False)

    fbr_invoice_number = fields.Char("FBR Invoice No", copy=False, tracking=True)
    fbr_irn = fields.Char("FBR IRN / UUID", copy=False, tracking=True)
    fbr_submission_date = fields.Datetime("FBR Submitted At", copy=False)
    fbr_last_error = fields.Text("FBR Last Error", copy=False)
    fbr_qr_code = fields.Binary("FBR QR Code", attachment=True, copy=False)

    def _is_fbr_applicable(self):
        self.ensure_one()
        return self.move_type in ('out_invoice', 'out_refund') and self.state in ('posted', 'draft')

    def _get_fbr_client(self):
        return self.env['fbr.client']

    def _prepare_fbr_payload(self):
        self.ensure_one()
        company = self.company_id
        ICP = self.env['ir.config_parameter'].sudo()

        # --- FIX: ensure InvoiceDate is a proper datetime before context_timestamp ---
        # invoice_date can be a date; convert to datetime and then localize by user context
        inv_dt_raw = self.invoice_date or fields.Datetime.now()
        inv_dt_dt = inv_dt_raw if isinstance(inv_dt_raw, datetime) else fields.Datetime.to_datetime(inv_dt_raw)
        inv_dt_local = fields.Datetime.context_timestamp(self, inv_dt_dt)
        invoice_date_str = inv_dt_local.strftime("%Y-%m-%d %H:%M:%S")

        def _taxes(line):
            tax_amount = 0.0
            tax_rate = 0.0
            for t in line.tax_ids:
                if t.amount_type == 'percent':
                    tax_rate += t.amount
                    tax_amount += line.price_subtotal * (t.amount / 100.0)
                else:
                    # If FBR needs non-percent taxes, map here accordingly.
                    pass
            return round(tax_rate, 2), round(tax_amount, 2)

        items = []
        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            rate, tax_amt = _taxes(line)
            items.append({
                "ItemCode": line.product_id.default_code or str(line.product_id.id),
                "ItemName": line.product_id.name,
                "Quantity": line.quantity,
                "UnitPrice": round(line.price_unit, 2),
                "Discount": round((line.discount or 0.0) * line.price_unit * line.quantity / 100.0, 2),
                "SalesTaxRate": rate,
                "SalesTaxAmount": tax_amt,
                "TotalAmount": round(line.price_total, 2),
            })

        buyer_ntn = self.partner_id.vat or ""
        buyer_cnic = self.partner_id.l10n_pk_cnic if hasattr(self.partner_id, "l10n_pk_cnic") else ""

        payload = {
            "InvoiceType": "Sale Invoice" if self.move_type == "out_invoice" else "Credit Note",
            "InvoiceDate": invoice_date_str,
            "POSID": ICP.get_param('fbr_pos_id') or "",
            "SellerNTN": ICP.get_param('fbr_registration_no') or (company.vat or ""),
            "SellerBusinessName": company.name,
            "SellerAddress": company.street or "",
            "SellerProvince": company.state_id.name if company.state_id else "",
            "BuyerNTN": buyer_ntn,
            "BuyerCNIC": buyer_cnic,
            "BuyerName": self.partner_id.name or "",
            "Items": items,
            "InvoiceTotal": round(self.amount_total, 2),
            "InvoiceTaxTotal": round(sum(i["SalesTaxAmount"] for i in items), 2),
            "PaymentMode": "Cash" if not self.invoice_payment_term_id else "Credit",
            "Currency": self.currency_id.name,
            "OdooMoveId": self.id,
            "OdooMoveName": self.name or "",
        }
        return payload

    def action_send_to_fbr(self):
        for move in self:
            if not move._is_fbr_applicable():
                continue
            client = move._get_fbr_client()
            payload = move._prepare_fbr_payload()
            log = move.env['fbr.invoice.log'].sudo().create({
                "move_id": move.id,
                "status": "pending",
                "request_json": json.dumps(payload, ensure_ascii=False, indent=2),
                "environment": client._get_env_key(),
            })
            try:
                result = client.submit_invoice(payload)
                # Expected result structure (adjust to real API):
                # { "success": True, "fbr_invoice_number": "...", "irn": "...",
                #   "qr_string": "....", "submitted_at": "2025-08-21T12:34:56" }
                if not result.get("success"):
                    raise Exception(result.get("message") or "FBR submission failed")

                move.write({
                    "fbr_state": "submitted",
                    "fbr_invoice_number": result.get("fbr_invoice_number") or result.get("invoice_number"),
                    "fbr_irn": result.get("irn") or result.get("uuid"),
                    "fbr_submission_date": fields.Datetime.now(),
                    "fbr_last_error": False,
                })
                qr_payload = result.get("qr_string") or ""
                if qr_payload:
                    qr_bin = client.make_qr_image(qr_payload)
                    move.fbr_qr_code = base64.b64encode(qr_bin)
                log.write({"status": "submitted", "response_json": json.dumps(result, ensure_ascii=False, indent=2)})
            except Exception as e:
                msg = str(e)
                move.write({"fbr_state": "failed", "fbr_last_error": msg})
                log.write({"status": "failed", "error_message": msg})
                ICP = self.env["ir.config_parameter"].sudo()
                if ICP.get_param("fbr_block_post_on_error") == "True":
                    raise UserError(_("FBR submission failed and blocking is enabled: %s") % msg)

    def action_cancel_fbr(self):
        for move in self:
            if move.fbr_state != "submitted":
                continue
            client = move._get_fbr_client()
            try:
                res = client.cancel_invoice({"invoice_number": move.fbr_invoice_number, "irn": move.fbr_irn})
                if res.get("success"):
                    move.write({"fbr_state": "cancelled"})
                else:
                    raise Exception(res.get("message") or "FBR cancel failed")
            except Exception as e:
                raise UserError(_("FBR cancel failed: %s") % str(e))

    def action_retry_fbr(self):
        for move in self.filtered(lambda m: m.fbr_state in ("failed", "not_submitted", "pending")):
            move.action_send_to_fbr()

    def action_post(self):
        res = super().action_post()
        ICP = self.env["ir.config_parameter"].sudo()
        if ICP.get_param("fbr_enabled") == "True":
            for move in self.filtered(lambda m: m.move_type in ("out_invoice", "out_refund")):
                move.action_send_to_fbr()
        return res
