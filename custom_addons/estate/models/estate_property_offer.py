"""Estate Property Offer model."""

from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class EstatePropertyOffer(models.Model):
    """Model for managing estate property offers."""
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False
    )
    partner_id = fields.Many2one('res.partner',
                                 required=True)
    property_id = fields.Many2one('estate.property',
                                  required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline",
                                inverse="_inverse_date_deadline",
                                store=True)
    property_type_id = fields.Many2one(related='property_id.estate_property_type_id',
                                       store=True,
                                       string='Property type')



    _sql_constraints = [
        ('check_offer_price_positive',
         'CHECK(price > 0)',
         'Offer price must be strictly positive.'),
    ]

    @api.depends('validity', 'create_date')
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Datetime.now()
            record.date_deadline = create_date.date() + timedelta(days=record.validity)

    @api.model_create_multi
    def create(self, vals_list):
        """Create new offers ensuring each offer price is not lower than existing offers
         for the same property.
            Raise Error: If a new offer price is lower than any existing offer price
            for the property.
            Update the property's state to 'offer_received' upon successful offer creation.
            """
        offers = super().create(vals_list)
        for offer in offers:
            existing_offers = offer.property_id.offer_ids.filtered(lambda o: o.id != offer.id)
            max_offer = max(existing_offers.mapped('price'), default=0.0)
            if offer.price < max_offer:
                raise ValidationError("You cannot create an offer lower than an existing one.")
            offer.property_id.state = 'offer_received'
        return offers

    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Datetime.now()
            record.validity = (record.date_deadline - create_date.date()).days

    def action_accept(self):
        """Accept the offer and update the related property with buyer and selling price.
            Ensures that only one offer can be accepted per property.
            """
        for offer in self:
            other_accepted = self.search([
                ('property_id', '=', offer.property_id.id),
                ('status', '=', 'accepted')
            ])
            if other_accepted:
                raise UserError("An offer has already been accepted for this property.")

            offer.status = 'accepted'
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.selling_price = offer.price
            offer.property_id.state = 'offer_accepted'


    def action_refuse(self):
        """Mark the offer as refused by updating its status."""
        for offer in self:
            offer.status = 'refused'
