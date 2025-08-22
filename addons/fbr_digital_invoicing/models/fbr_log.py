from odoo import models, fields

class FBRInvoiceLog(models.Model):
    _name = "fbr.invoice.log"
    _description = "FBR Invoice Submission Log"
    _order = "create_date desc"

    move_id = fields.Many2one("account.move", string="Invoice", index=True, ondelete="cascade")
    status = fields.Selection([
        ("pending", "Pending"),
        ("submitted", "Submitted"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ], default="pending", required=True)
    request_json = fields.Text("Request JSON")
    response_json = fields.Text("Response JSON")
    error_message = fields.Text("Error")
    environment = fields.Selection([("sandbox", "Sandbox"), ("production", "Production")], default="sandbox")