# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
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

    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True,
    )

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for rec in self:
            base_dt = rec.create_date or fields.Datetime.now()
            base_date = fields.Date.to_date(base_dt)
            rec.date_deadline = base_date + relativedelta(days=rec.validity or 0)

    def _inverse_date_deadline(self):
        for rec in self:
            if rec.date_deadline:
                base_dt = rec.create_date or fields.Datetime.now()
                base_date = fields.Date.to_date(base_dt)
                delta = rec.date_deadline - base_date
                rec.validity = max(delta.days, 0)

    # ---------- NEW: Action Methods ----------
    def action_accept(self):
        for rec in self:
            if rec.property_id.state == "sold":
                raise UserError("This property is already sold.")
            # reset other offers
            other_offers = rec.property_id.offer_ids - rec
            other_offers.write({"status": "refused"})
            # set buyer & price
            rec.property_id.buyer_id = rec.partner_id
            rec.property_id.selling_price = rec.price
            rec.property_id.state = "offer_accepted"
            rec.status = "accepted"
        return True

    def action_refuse(self):
        for rec in self:
            rec.status = "refused"
        return True
