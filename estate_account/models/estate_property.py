# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.fields import Command

class InheritedModel(models.Model):
    _inherit = "estate.property"

    def action_inherited(self):
        return super().action_inherited()

    def action_sold(self):
        print("DEBUG: estate_account-action_sold called")
        for property in self:
            self.env["account.move"].create({
                "partner_id": property.buyer_id.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create({
                        "name": "6% commission",
                        "quantity": 1,
                        "price_unit": property.selling_price * 0.06,
                    }),
                    Command.create({
                        "name": "administrative fees",
                        "quantity": 1,
                        "price_unit": 100.00,
                    }),
                ],
            })

        return super().action_sold()