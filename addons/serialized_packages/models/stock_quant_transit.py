from odoo import models, fields
from odoo.exceptions import UserError
from collections import defaultdict

class StockQuantTransitWizard(models.TransientModel):
    _name = 'stock.quant.transit.wizard'
    _description = 'Vận chuyển lên xe'

    vehicle_id = fields.Many2one('vehicle.management', string='Biển số xe', required=True)
    date = fields.Datetime(string="Giờ khởi hành", required=True, default=lambda self: fields.Datetime.now())
    driver_name = fields.Char(string="Tên tài xế")
    vehicle_info = fields.Char(string="Thông tin xe")

    def action_confirm(self):
        StockQuant = self.env['stock.quant']
        StockPicking = self.env['stock.picking']
        StockMove = self.env['stock.move']

        quant_ids = self.env.context.get('active_ids', [])
        if not quant_ids:
            raise UserError("Không có dòng nào được chọn để xuất kho!")

        selected_quants = StockQuant.browse(quant_ids)

        location_id = selected_quants.mapped('location_id')
        location_id = location_id[0]

        warehouse = self.env['stock.warehouse'].search([
            ('view_location_id', 'parent_of', location_id.id)
        ], limit=1)

        if not warehouse:
            raise UserError("Không tìm thấy kho hàng phù hợp cho địa điểm này!")

        location_id = warehouse.lot_stock_id

        location_code = warehouse.lot_stock_id.complete_name or ''
        if location_code.startswith('HN'):
            partner_id = 8
        elif location_code.startswith('KG'):
            partner_id = 7

        picking_type = self.env['stock.picking.type'].search([
            ('warehouse_id', '=', warehouse.id),
            ('code', '=', 'outgoing')
        ], limit=1)

        if not picking_type:
            raise UserError("Không tìm thấy loại chứng từ kho xuất phù hợp với kho hiện tại!")


        product_quantities = defaultdict(float)
        for quant in selected_quants:
            product_quantities[
                (quant.product_id.id,
                quant.product_id.uom_id.id,
                quant.owner_id.id,
                quant.consignment_packed_type,
                quant.unit_of_measure)
            ] += quant.quantity

        incoming_picking_names = set()

        for quant in selected_quants:
            move_lines = self.env['stock.move.line'].search([('product_id', '=', quant.product_id.id),
                                                            ('location_dest_id', '=', quant.location_id.id)])
            for move_line in move_lines:
                move = move_line.move_id
                if move.picking_id and move.picking_id.picking_type_id.code == 'incoming':
                    incoming_picking_names.add(move.picking_id.name)

        transit_location = self.env['stock.location'].search([
            ('complete_name', '=', 'Địa điểm ảo/Xe vận chuyển')
        ], limit=1)

        if not transit_location:
            raise UserError("Không tìm thấy địa điểm trung chuyển 'Địa điểm ảo/Xe vận chuyển'!")
        picking_vals = {
            'partner_id': partner_id,
            'picking_type_id': picking_type.id, 
            'location_id': location_id.id,
            'location_dest_id': transit_location.id,  
            'scheduled_date': self.date,
            'move_ids_without_package': [],
            'ten_tai_xe': self.driver_name,
            'thong_tin_xe': self.vehicle_info,
            # 'bien_so_xe': f"{str(self.vehicle_id.license_plate)}-{str(self.date)}",
            'bien_so_xe': f"{str(self.vehicle_id.license_plate)}",
            'is_transit_out': True,
        }
        picking = StockPicking.create(picking_vals)

        move_dict = {}

        for (product_id, uom_id, owner_id, consignment_packed_type, unit_of_measure), quantity in product_quantities.items():
            existing_move = move_dict.get((product_id, uom_id, owner_id, consignment_packed_type, unit_of_measure))
            
            if not existing_move:
                move_vals = {
                    'picking_id': picking.id,
                    'name': self.env['product.product'].browse(product_id).display_name,
                    'product_id': product_id,
                    'product_uom_qty': quantity,
                    'product_uom': uom_id,
                    'location_id': location_id.id,
                    'location_dest_id': transit_location.id,
                    'consignment_packed_type': consignment_packed_type,
                    'unit_of_measure': unit_of_measure,
                }
                move = StockMove.create(move_vals)
                move_dict[(product_id, uom_id, owner_id, consignment_packed_type, unit_of_measure)] = move
            else:
                existing_move.product_uom_qty += quantity

        # for quant in selected_quants:
        #     move_line_vals = {
        #         'move_id': move_dict[(quant.product_id.id,
        #                             quant.product_id.uom_id.id,
        #                             quant.owner_id.id,
        #                             quant.consignment_packed_type,
        #                             quant.unit_of_measure)].id,
        #         'product_id': quant.product_id.id,
        #         'qty_done': 0.0,
        #         'product_uom_id': quant.product_id.uom_id.id,
        #         'location_id': quant.location_id.id,
        #         'owner_id': quant.owner_id.id,
        #         'location_dest_id': transit_location.id,
        #         'lot_id': quant.lot_id.id if quant.lot_id else False,
        #     }
        #     StockMoveLine.create(move_line_vals)

        picking.action_confirm()
        picking.action_assign()

        for move in picking.move_ids:
            for move_line in move.move_line_ids:
                move_line.consignment_packed_type = move.consignment_packed_type
                move_line.unit_of_measure = move.unit_of_measure

        view_id = False
        if picking.partner_id.id == 7:
            view_id = self.env.ref('consignment.stock_picking_form_view').id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': picking.id,
            'target': 'current',
            **({'view_id': view_id} if view_id else {})
        }

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}