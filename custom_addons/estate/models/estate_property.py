# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Estate Property model."""
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero



class EstateProperty(models.Model):
    """Estate Property main model."""
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False,
                                    default=lambda self: date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True,copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden =fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Type',
        selection=[('north','North'),
                   ('south','South'),
                   ('east','East'),
                   ('west','West')
                   ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        required=True,
        copy=False,
        default='new'
    )
    estate_property_type_id = fields.Many2one("estate.property.type", string="Estate Property Type")
    buyer_id = fields.Many2one("res.partner",
                               string="Buyer",
                               copy=False)
    salesperson_id =fields.Many2one("res.users",
                                    string="Salesman",
                                    default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag",
                               string="Tags")
    offer_ids = fields.One2many('estate.property.offer',
                                'property_id',
                                string='Offers')
    total_area = fields.Float(compute="_compute_total_area",
                              store=True)
    best_price = fields.Float(compute="_compute_best_price",
                              string="Best offer",
                              store=True)

    _sql_constraints = [
        ('check_expected_price_positive',
         'CHECK(expected_price > 0)',
         'Expected price must be positive.'),
        ('check_selling_price_positive',
         'CHECK(selling_price >= 0)',
         'Selling price must be positive.'),
    ]

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped('price')
            record.best_price = max(prices) if prices else 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price_margin(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue
            min_allowed = record.expected_price * 0.9
            if float_compare(record.selling_price, min_allowed, precision_digits=2) < 0:
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price."
                )

    def action_cancel(self):
        """Mark the property as canceled unless it's already sold."""
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold properties cannot be canceled.")
            record.state = 'canceled'

    def action_sold(self):
        """Mark the property as sold unless it's canceled."""
        for record in self:
            if record.state == 'canceled':
                raise UserError("Canceled properties cannot be marked as sold.")
            record.state = 'sold'

    def unlink(self):
        """Prevent deletion unless property is in 'New' or 'Cancelled' state."""
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise UserError("You can only delete properties in 'New' or 'Cancelled' state.")
        return super().unlink()
