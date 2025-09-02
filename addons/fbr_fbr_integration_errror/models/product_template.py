from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fbr_hs_code = fields.Char(
        string="FBR HS Code",
        help="e.g., 3303.0010 for perfumes, etc."
    ) 
    fbr_rate_text = fields.Char(
        string="FBR Rate (text)",
        help="e.g., 18% per DI spec 'rate' string"
    )
    fbr_uom_text = fields.Char(
        string="FBR UoM Text",
        default="Numbers, pieces, units"
    )
    
    fbr_sale_type = fields.Selection(
        [
            ("standard", "Goods at standard rate (default)"),
            ("zero", "Zero-rated goods"),
            ("exempt", "Exempt goods"),
            ("reduced", "Reduced rate goods"),
        ],
        string="FBR Sale Type",
        default="standard"
    )
    fbr_sro_schedule_no = fields.Char(
        string="FBR SRO Schedule No"
    )
    fbr_sro_item_serial_no = fields.Char(
        string="FBR SRO Item Serial No"
    )

    # Additional taxes per product (optional, per DI fields)
    fbr_extra_tax = fields.Char(
        string="Extra Tax (text)",
        help="Leave blank if not applicable"
    )
    fbr_further_tax = fields.Float(
        string="Further Tax",
        help="Numeric value to send in items[].furtherTax"
    )
    fbr_fixed_notified_value = fields.Float(
        string="Fixed/Notified Value or Retail Price"
    )

    # Mapping helper: describe product category for reporting
    fbr_category_hint = fields.Selection(
        [
            ("perfume", "Perfume"),
            ("candle", "Scented Candle"),
            ("fabric", "Bourne/Waxed Fabric"),
            ("other", "Other"),
        ],
        string="FBR Category Hint",
        default="other"
    )