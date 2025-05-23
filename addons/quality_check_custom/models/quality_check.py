from odoo import models, fields

class QualityCheck(models.Model):
    _inherit = 'quality.check'

    list_loi = fields.Selection([
        ('Khác màu (đậm, nhạt)', 'Khác màu (đậm, nhạt)'),
        ('In nháy chữ, bóng chữ, mất nét', 'In nháy chữ, bóng chữ, mất nét'),
        ('Sai maket', 'Sai maket'),
        ('Chấm trắng/ chấm đen', 'Chấm trắng/ chấm đen'),
        ('Xước, nháy, nhòe mực', 'Xước, nháy, nhòe mực'),
        ('Bế lệch/ bế sâu/ không đứt', 'Bế lệch/ bế sâu/ không đứt'),
        ('In lệch', 'In lệch'),
        ('Bung bản, nứt bản', 'Bung bản, nứt bản'),
        ('In không khô mực, bong mực ', 'In không khô mực, bong mực '),
        ('Bong mực ép nhũ', 'Bong mực ép nhũ'),
        ('Sai kích thước ', 'Sai kích thước '),
        ('Sai tiêu chuẩn, bản, yêu cầu sản xuất', 'Sai tiêu chuẩn, bản, yêu cầu sản xuất'),
        ('Rộp màng, bong tem, nhăn tem', 'Rộp màng, bong tem, nhăn tem'),
        ('Dị vật , bụi, loang ', 'Dị vật , bụi, loang '),
        ('Xén lệch', 'Xén lệch'),
        ('Sai số nhảy', 'Sai số nhảy'),
        ('Lôĩ khác ', 'Lôĩ khác '),
    ], string='List lỗi')
