from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    khach_hang = fields.Many2one('res.partner', string='Khách hàng', copy=True)
    phan_loai_san_pham = fields.Selection([('Nhãn dán', 'Nhãn dán')], string='Phân loại sản phẩm', copy=True)
    mo_ta = fields.Char(string='Mô tả', copy=True)
    chieu_dai = fields.Float(string='Chiều dài (mm)', copy=True)
    chieu_rong = fields.Float(string='Chiều rộng', copy=True)
    pd = fields.Float(string='P/D', copy=True)
    cavity_hang = fields.Float(string='Cavity hàng', copy=True)
    cavity_cot = fields.Float(string='Cavity cột', copy=True)
    khoang_cach_hang = fields.Float(string='Khoảng cách hàng', copy=True)
    khoang_cach_cot = fields.Float(string='Khoảng cách cột', copy=True)
    khoang_cach_toi_liner_trai = fields.Float(string='Khoảng cách tới liner trái', copy=True)
    khoang_cach_toi_liner_phai = fields.Float(string='Khoảng cách tới liner phải', copy=True)
    huong_cuon = fields.Selection([('Hàng ở mặt ngoài', 'Hàng ở mặt ngoài'), ('Hàng ở mặt trong', 'Hàng ở mặt trong')], string='Hướng cuộn', copy=True)
    loai_dao = fields.Selection([('PVC', 'PVC'), ('Từ', 'Từ'), ('Trục', 'Trục')], string='Loại dao', copy=True)
    tuoi_dao = fields.Float(string='Tuổi dao (Số dập)', copy=True)
    buoc_dao = fields.Float(string='Bước dao', copy=True)
    so_mau = fields.Float(string='Số màu', copy=True)
    quy_cach_dong_goi = fields.Selection(
        [('Cuộn', 'Cuộn'), ('Tờ', 'Tờ')],
        string='Quy cách đóng gói',
        copy=True,
        required=True,  # Make the field not nullable
        default='Tờ'    # Set the default value to "Tờ"
    )
    don_vi = fields.Many2one('uom.uom', string='Đơn vị', copy=True)
    so_luong_dong_goi = fields.Float(string='Số lượng đóng gói', copy=True)
    ban_ve = fields.Binary(string='Bản vẽ', copy=True)
    kho_nvl_chinh = fields.Float(string='Khổ NVL chính (mm)', copy=True)
    kho_nvl_phu = fields.Float(string='Khổ NVL phụ (mm)', copy=True)
    buoc_dao = fields.Float(string='Bước dao', copy=True)
    so_mau = fields.Float(string='Số màu', copy=True)

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    chieu_dai = fields.Float(related='bom_id.chieu_dai', string='Chiều dài (mm)', readonly=True)
    chieu_rong = fields.Float(related='bom_id.chieu_rong', string='Chiều rộng', readonly=True)
    khoang_cach_hang = fields.Float(related='bom_id.khoang_cach_hang', string='Khoảng cách hàng', readonly=True)
    cavity_cot = fields.Float(related='bom_id.cavity_cot', string='Cavity cột', readonly=True)
    bom_qty = fields.Float(string='BOM Quantity', related='bom_id.product_qty', readonly=True)
    product_qty = fields.Float(string='Product Quantity', compute='_compute_product_qty', store=True)

    @api.depends('chieu_dai', 'khoang_cach_hang', 'cavity_cot', 'bom_qty')
    def _compute_product_qty(self):
        for line in self:
            if line.cavity_cot != 0:
                total_length = line.chieu_dai + line.khoang_cach_hang
                length_in_meters = total_length / 1000
                total_qty = length_in_meters * line.bom_qty
                line.product_qty = total_qty / line.cavity_cot
            else:
                line.product_qty = 0


    # @api.model
    # def create(self, vals):
    #     record = super(MrpBomLine, self).create(vals)
    #     return record

    # def write(self, vals):
    #     res = super(MrpBomLine, self).write(vals)
    #     return res