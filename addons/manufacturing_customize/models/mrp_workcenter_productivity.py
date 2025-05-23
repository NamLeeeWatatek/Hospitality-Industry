from odoo import models, fields, api

class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    raw_material = fields.Many2one(
        'product.product',
        string="Nguyên liệu",
        domain="[('id', 'in', allowed_raw_material_ids)]"
    )

    allowed_raw_material_ids = fields.Many2many(
        'product.product',
        compute="_compute_allowed_raw_material_ids",
        store=False
    )


    consumption = fields.Float(
        string="Tiêu thụ",
        store=True,
        digits='Product Unit of Measure',
        help="Số lượng tiêu thụ của nguyên liệu được chọn trong công đoạn."
    )

    @api.depends('workorder_id')
    def _compute_allowed_raw_material_ids(self):
        for record in self:
            if record.workorder_id:
                record.allowed_raw_material_ids = record.workorder_id.move_raw_ids.mapped('product_id')
