from odoo import models, fields
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_picking_type(self, code, company_id):
        """Tìm kiếm loại phiếu nhập kho theo mã và công ty."""
        picking_type = self.env['stock.picking.type'].sudo().search([
            ('code', '=', code),
            ('company_id', '=', company_id),
        ], limit=1)
        if not picking_type:
            raise UserError(f"Không tìm thấy loại phiếu {code} kho phù hợp!")
        return picking_type

    def _get_warehouse(self, company_id, code):
        """Tìm kho theo công ty và mã kho."""
        warehouse = self.env['stock.warehouse'].sudo().search([
            ('company_id', '=', company_id),
            ('code', '=', code),
        ], limit=1)
        if not warehouse:
            raise UserError(f"Không tìm thấy kho với mã {code} trong công ty!")
        return warehouse

    def _create_picking(self, picking, picking_type, warehouse, company_id):
        """Tạo phiếu nhập kho từ phiếu xuất kho."""
        stock_location = warehouse.lot_stock_id
        return self.sudo().create({
            'picking_type_id': picking_type.id,
            'partner_id': picking.partner_id.id if picking.partner_id else picking.picking_type_id.warehouse_id.partner_id.id,
            'location_id': picking.location_dest_id.id,
            'location_dest_id': stock_location.id,
            'origin': picking.name,
            'scheduled_date': fields.Datetime.now(),
            'state': 'draft',
            'company_id': company_id,
            'ten_tai_xe': picking.ten_tai_xe,
            'thong_tin_xe': picking.thong_tin_xe,
            'bien_so_xe': picking.bien_so_xe,
        })

    def _create_move(self, picking, move, new_picking, picking_type, company_id):
        """Tạo di chuyển sản phẩm cho phiếu nhập kho và áp dụng Putaway Rule nếu có."""
        product = move.product_id
        quantity = move.product_uom_qty
        location = new_picking.location_dest_id

        putaway_location = location._get_putaway_strategy(product, quantity)

        new_move = self.env['stock.move'].sudo().create({
            'picking_id': new_picking.id,
            'product_id': product.id,
            'name': product.display_name,
            'product_uom_qty': quantity,
            'product_uom': move.product_uom.id,
            'location_id': picking.location_dest_id.id,
            'location_dest_id': putaway_location.id if putaway_location else location.id,
            'company_id': company_id,
            'consignment_packed_type': move.consignment_packed_type,
            'unit_of_measure': move.unit_of_measure,
        })

        if not move.move_line_ids and move.state != 'done':
            move._action_assign()

        self._create_move_lines(move, new_move, picking, picking_type)

    def _create_move_lines(self, move, new_move, picking, picking_type):
        """Tạo dòng di chuyển cho sản phẩm, bao gồm kiểm tra tracking của lot."""
        for line in move.move_line_ids:
            if move.product_id.tracking == 'lot' and line.lot_id:
                self._create_lot_move_line(line, move, new_move, picking, picking_type)
            else:
                self.env['stock.move.line'].sudo().create({
                    'move_id': new_move.id,
                    'product_id': line.product_id.id,
                    'qty_done': line.qty_done or move.product_uom_qty,
                    'location_id': picking.location_dest_id.id,
                    'location_dest_id': None,
                    'owner_id': line.owner_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'company_id': new_move.company_id.id,
                    'unit_of_measure': move.unit_of_measure,
                    'consignment_packed_type': move.consignment_packed_type,
                })

    def _create_lot_move_line(self, line, move, new_move, picking, picking_type):
        """Tạo dòng di chuyển với tracking lot."""
        existing_lot = self.env['stock.lot'].sudo().search([
            ('name', '=', line.lot_id.name),
            ('product_id', '=', move.product_id.id),
            ('company_id', '=', new_move.company_id.id),
        ], limit=1)

        if not existing_lot:
            existing_lot = self.env['stock.lot'].sudo().search([
                ('name', '=', line.lot_id.name),
                ('product_id', '=', move.product_id.id),
            ], limit=1)

            if existing_lot and existing_lot.company_id: #False lot serial để by pass qua quyền đa công ty
                existing_lot.write({'company_id': False})

        self.env['stock.move.line'].sudo().create({
            'move_id': new_move.id,
            'product_id': line.product_id.id,
            'qty_done': line.qty_done or move.product_uom_qty,
            'lot_id': existing_lot.id,
            'lot_name': existing_lot.name,
            'owner_id': line.owner_id.id,
            'location_id': picking.location_dest_id.id,
            'location_dest_id': new_move.location_dest_id.id,
            'product_uom_id': line.product_uom_id.id,
            'company_id': new_move.company_id.id,
            'unit_of_measure': move.unit_of_measure,
            'consignment_packed_type': move.consignment_packed_type,
        })

    def create_incoming_transfer(self):
        """Tạo phiếu nhập kho tự động từ phiếu xuất kho (hàng nhà)."""
        for picking in self:
            if picking.picking_type_id.id != 2 or picking.picking_type_id.code != 'outgoing':
                continue

            incoming_picking_type = self._get_picking_type('incoming', 3)
            cambodia_warehouse = self._get_warehouse(3, 'HN')
            incoming_picking = self._create_picking(picking, incoming_picking_type, cambodia_warehouse, 3)

            for move in picking.move_ids_without_package:
                self._create_move(picking, move, incoming_picking, incoming_picking_type, 3)

    def create_consignment_transfer(self):
        """Tạo phiếu nhập kho ký gửi tự động từ phiếu xuất kho ký gửi."""
        for picking in self:
            if picking.picking_type_id.id != 10 or picking.picking_type_id.code != 'outgoing':
                continue

            consignment_picking_type = self._get_picking_type('incoming', 2)
            consignment_warehouse = self._get_warehouse(2, 'KG')
            consignment_picking = self._create_picking(picking, consignment_picking_type, consignment_warehouse, 2)

            for move in picking.move_ids_without_package:
                self._create_move(picking, move, consignment_picking, consignment_picking_type, 2)

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        self.create_incoming_transfer()
        self.create_consignment_transfer()

        for picking in self:
            if picking.picking_type_id.code == 'incoming' and picking.company_id.id in [2, 3]:
                quants = self.env['stock.quant'].sudo().search([
                    ('location_id', '=', picking.location_dest_id.id),
                    ('product_id', 'in', picking.move_ids_without_package.mapped('product_id').ids)
                ])
                quants.write({'packed_status': 'cam_warehouse'})

        return res