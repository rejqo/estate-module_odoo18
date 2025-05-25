# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Estate Property Tag model."""

from odoo import models, fields

# pylint: disable=too-few-public-methods
class EstatePropertyTag(models.Model):
    """Model representing tags for estate properties."""
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)', 'Tag name must be unique.'),
    ]
