# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    Message = fields.Char(string="Message")  # Thêm trường Message

    # @api.constrains('quantity')
    # def _check_quantity(self):
    #     for record in self:
    #         if record.quantity > record.product_uom_qty:
    #             raise ValidationError("Số lượng thực tế không được lớn hơn nhu cầu!")

    # def write(self, vals):
    #     if 'quantity' in vals:
    #         new_qty = vals.get('quantity')
    #         for record in self:
    #             if new_qty > record.product_uom_qty:
    #                 raise ValidationError("Số lượng thực tế không được lớn hơn nhu cầu!")
    #     return super(StockMove, self).write(vals)

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get('quantity') and vals.get('quantity') > vals.get('product_uom_qty', 0):
    #             raise ValidationError("Số lượng thực tế không được lớn hơn nhu cầu!")
    #     return super(StockMove, self).create(vals_list)