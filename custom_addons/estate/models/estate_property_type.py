"""Estate property type model."""

from odoo import models, fields, api

# pylint: disable=too-few-public-methods
class EstatePropertyType(models.Model):
    """Model for property types in the estate module."""
    _name = 'estate.property.type'
    _description = 'Property Type'
    _order = "sequence, name"

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property','estate_property_type_id','properties')
    sequence = fields.Integer('sequence', default =10)
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='offers')
    offer_count = fields.Integer(string='Offer count', compute='_compute_offer_count')

    _sql_constraints = [
        ('unique_property_type_name', 'UNIQUE(name)', 'Property type name must be unique.'),
    ]

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
