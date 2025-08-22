# FBR Digital Invoicing (PK) for Odoo 17/18

**Disclaimer:** Real FBR endpoints, payload fields, and response shapes must be verified against the official FBR Technical API documentation. This module provides a clean integration scaffold, fields on invoices, API client, logging, QR generation, report injection, and sandbox/production switching.

## Quick start

1. Copy `fbr_digital_invoicing` into your Odoo addons path.
2. (Optional) Run the included mock server to simulate FBR:
   ```bash
   cd fbr_mock_server
   pip install -r requirements.txt
   python app.py
   ```
3. In Odoo, Update Apps list and install *FBR Digital Invoicing (PK)*.
4. Go to Settings → FBR Integration, enable it, set Sandbox URLs to the mock server (defaults are already localhost), and put any dummy keys.
5. Create a customer invoice, post it, and click **Send to FBR** (or let auto-submit on post). You should see FBR fields fill and a QR show up.
6. Replace endpoints/keys with real FBR credentials for production.

## Dependencies
- Python: `requests`, `qrcode[pil]` or PIL (Pillow). Odoo image field rendering uses base64 PNGs we generate.
- If QR libs are missing, a fallback placeholder PNG is produced.

## Fields on Invoice
- FBR Status, Invoice No, IRN/UUID, Submitted At, Last Error, QR Code.

## XML Report
Extends standard invoice report to show FBR block and QR.

## Logs
Model `fbr.invoice.log` stores request/response/error per submission.

## Cron
Hourly retry of failed/pending invoices.