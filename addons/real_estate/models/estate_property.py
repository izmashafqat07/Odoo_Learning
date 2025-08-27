# /home/$USER/src/tutorials/estate/models/estate_property.py
from odoo import models, fields
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    # Reserved fields
    active = fields.Boolean(default=True)  # hide inactive in searches; default True so it doesn’t disappear
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        required=True,
        copy=False,
        default="new",
    )

    # Basic fields (simple types)
    name = fields.Char(string="Title", required=True, index=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")

    # Not copied when duplicating
    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: (fields.Date.context_today(self) + relativedelta(months=3)),
    )

    expected_price = fields.Float(string="Expected Price", required=True)

    # Read-only and not copied
    selling_price = fields.Float(string="Selling Price", copy=False)

    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")

    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")

    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        string="Garden Orientation",
        help="Direction the garden faces.",
    )
