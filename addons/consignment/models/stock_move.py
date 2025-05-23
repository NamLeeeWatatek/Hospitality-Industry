from odoo import models, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        fields = super()._prepare_merge_moves_distinct_fields()
        fields.append('consignment_packed_type')
        fields.append('unit_of_measure')
        return fields
