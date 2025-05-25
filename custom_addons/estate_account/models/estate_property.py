# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, api
from odoo.cli import Command


class InhertedModel(models.Model):
    _inherit = "inherited.model"

    def action_inherited(self):
        return super().action_inherited()

    def action_sold(self):
        print("DEBUG: estate_account-action_sold called")
        for property in self:
            self.env["acount.move"].create({
                "partner_id": property.buyer_id.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create({
                        'name': '6% commission',
                        'quatity': 1,
                        'price_unit': property.selling_price * 0.06,
                    }),
                    Command.create({
                        "name": "administrative fees",
                        "quantity": 1,
                        "price_unit": 100.00,
                    })
                ],
            })
        return super().action_sold()


