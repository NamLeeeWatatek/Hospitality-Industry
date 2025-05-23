from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"
    _rec_name = "display_name"

    phone = fields.Char(required=True)

    def name_get(self):
        """Hiển thị kết quả tìm kiếm dưới dạng 'Phone - Name'"""
        result = []
        for record in self:
            phone_part = record.phone or record.mobile or "No Phone"
            name = f"{phone_part} - {record.name}"
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Chỉ tìm kiếm theo số điện thoại (phone, mobile)"""
        args = args or []
        if name:
            partners = self.search(
                ["|", ("phone", operator, name), ("mobile", operator, name)] + args, limit=limit
            )
        else:
            partners = self.search(args, limit=limit)
        return partners.name_get()
    
    def _compute_display_name(self):
        for record in self:
            phone_part = f"{record.phone} - " if record.phone else ""
            record.display_name = f"{phone_part}{record.name}"

    display_name = fields.Char(compute="_compute_display_name", store=True)
