# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta  # already used for date_availability

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

    # ---------- NEW: Computed fields ----------
    total_area = fields.Integer(
        string="Total Area (sqm)",
        compute="_compute_total_area",
        store=True,  # set to False if you don't want DB storage
    )
    best_price = fields.Float(
        string="Best Offer",
        compute="_compute_best_price",
        store=True,  # set to False if you don't want DB storage
    )

    # Chapter 7: Relations
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user.id
    )
    offer_ids = fields.One2many(
        "estate.property.offer", "property_id", string="Offers"
    )

    # ---------- NEW: Compute methods ----------
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = (rec.living_area or 0) + (rec.garden_area or 0)

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for rec in self:
            prices = rec.offer_ids.mapped("price")
            rec.best_price = max(prices) if prices else 0.0

    # ---------- NEW: Onchange ----------
    @api.onchange("garden")
    def _onchange_garden(self):
        # Form-only helper: don't add business rules here
        if self.garden:
            if not self.garden_area:
                self.garden_area = 10  # default suggestion
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False
