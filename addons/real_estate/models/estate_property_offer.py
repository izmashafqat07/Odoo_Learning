# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"

    price = fields.Float(string="Price")
    status = fields.Selection(
        [
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        string="Status",
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)

    # ---------- NEW: validity + date_deadline ----------
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True,  # store for filtering/sorting in views
    )

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        """
        date_deadline = (create_date or now) + validity days
        Use fallback at creation time when create_date is not yet set.
        """
        for rec in self:
            base_dt = rec.create_date or fields.Datetime.now()
            base_date = fields.Date.to_date(base_dt)  # convert to date
            days = rec.validity or 0
            rec.date_deadline = base_date + relativedelta(days=days)

    def _inverse_date_deadline(self):
        """
        If user sets date_deadline, recompute validity = days between (deadline - base_date).
        base_date = create_date or today.
        """
        for rec in self:
            if rec.date_deadline:
                base_dt = rec.create_date or fields.Datetime.now()
                base_date = fields.Date.to_date(base_dt)
                delta = rec.date_deadline - base_date
                # keep non-negative; remove max(...) if you want to allow negative
                rec.validity = max(delta.days, 0)
