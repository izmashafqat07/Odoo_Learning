# -*- coding: utf-8 -*-
from odoo import models, fields
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    # Reserved fields
    active = fields.Boolean(default=True)
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

    # Basic fields
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

    # Not copied (read-only behavior can be handled in the view)
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

    # -----------------------
    # Chapter 7: Relations
    # -----------------------

    # Many2one: Property Type
    property_type_id = fields.Many2one(
        "estate.property.type",
        string="Property Type",
    )

    # Many2many: Tags
    tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Tags",
    )

    # Many2one: Buyer (res.partner) - do not copy on duplicate
    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False,
    )

    # Many2one: Salesperson (res.users) - default = current user
    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user.id,
    )

    # One2many: Offers (inverse of offer.property_id)
    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers",
    )
