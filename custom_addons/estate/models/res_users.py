# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
"""Extension of res.users to add property_ids field for estate module."""
from odoo import models, fields

# pylint: disable=too-few-public-methods
class Inherited(models.Model):
    """Extend res.users to add related estate properties."""
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.property',
                                   'salesperson_id',
                                   string='Properties',
                                   domain=[('state', '=', 'new')])
