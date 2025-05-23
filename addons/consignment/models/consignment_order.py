from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class ConsignmentOrder(models.Model):
    _inherit = 'sale.order'

    is_consignment_order = fields.Boolean(string="Is Consignment Order", default=False)

    consignment_fee_collector = fields.Selection(
        selection=[
            ('hcm', 'Hồ Chí Minh'),
            ('campuchia', 'Campuchia')
        ],
        string="Consignment Fee Collector",
        required=True,
        default='hcm'
    )

    recipient_id = fields.Many2one('res.partner', string="Recipient", help="Người gửi hàng ký gửi")
    sale_id_stock_picking_count = fields.Integer(string="Receipt", compute="_compute_sale_id_stock_picking_count")
    sale_id_stock_picking_delivery_count = fields.Integer(string="Delivery", compute="_compute_sale_id_stock_picking_delivery_count")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.is_consignment_order:
                record.name = self.env['ir.sequence'].next_by_code('sale.order.consignment') or '/'
        return records

    def action_confirm(self):
        """ Xử lý đơn ký gửi: ngăn tạo phiếu xuất, tạo phiếu nhập và đổi trạng thái thành 'sale' """
        for order in self:
            if order.is_consignment_order:
                # Khóa đơn hàng để tránh race condition khi nhiều user đồng thời confirm
                order = self.env['sale.order'].browse(order.id)

                # Kiểm tra lại trạng thái trước khi xử lý
                if order.state != 'draft':
                    raise UserError("Đơn hàng này đã được xử lý bởi người dùng khác. Vui lòng làm mới trang và thử lại.")

                # Xóa stock.move nếu đã bị tạo trước khi confirm
                moves = self.env['stock.move'].search([('origin', '=', order.name)])
                if moves:
                    moves.unlink()

                # Xóa stock.picking (phiếu xuất) nếu đã bị tạo trước khi confirm
                pickings = self.env['stock.picking'].search([
                    ('origin', '=', order.name),
                    ('picking_type_id.code', '=', 'outgoing')
                ])
                if pickings:
                    pickings.unlink()

                # Tạo phiếu nhập kho (cho hàng ký gửi)
                order._create_consignment_picking()

                # Đổi trạng thái
                order.state = 'sale'
                return True

        return super(ConsignmentOrder, self.filtered(lambda order: not order.is_consignment_order)).action_confirm()

    def _check_consignment_received(self):
        for order in self:
            if not order.is_consignment_order:
                continue

            order_lines = order.order_line.filtered(lambda l: l.product_id and l.product_uom_qty > 0)
            all_received = all(line.received_qty >= line.product_uom_qty for line in order_lines)

            pickings_done = self.env['stock.picking'].search([
                ('origin', '=', order.name),
                ('picking_type_id.code', '=', 'outgoing'),
                ('state', '=', 'done')
            ])

            if all_received and not pickings_done:
                order.delivery_status = 'pending'
            elif pickings_done:
                if all(line.consignment_delivered_qty >= line.product_uom_qty for line in order_lines):
                    order.delivery_status = 'full'
                elif any(line.consignment_delivered_qty > 0 for line in order_lines):
                    order.delivery_status = 'partial'
                else:
                    order.delivery_status = 'started'
    
    def action_view_receipt(self):
        """ Hiển thị danh sách phiếu nhập kho của đơn hàng này """
        pickings = self.env['stock.picking'].search([
            ('origin', '=', self.name),
            ('picking_type_id.code', '=', 'incoming')
        ])

        if not pickings:
            return {'type': 'ir.actions.act_window_close'}

        if len(pickings) == 1:

            return {
                'name': "Phiếu Nhập Kho",
                'view_mode': 'form',
                'view_id': self.env.ref('consignment.stock_picking_form_view').id,
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'res_id': pickings.id,
            }
        
        action = self.env.ref('stock.stock_picking_action_picking_type').read()[0] 
        action['domain'] = [('id', 'in', pickings.ids)] 
        return action

    def action_view_consignment_delivery(self):
        """ Hiển thị danh sách phiếu xuất kho của đơn hàng này """
        pickings = self.env['stock.picking'].search([
            ('origin', '=', self.name),
            ('picking_type_id.code', '=', 'outgoing')
        ])

        if not pickings:
            return {'type': 'ir.actions.act_window_close'}

        if len(pickings) == 1:
            return {
                'name': "Phiếu Giao Hàng",
                'view_mode': 'form',
                'view_id': self.env.ref('consignment.stock_picking_form_view').id,
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'res_id': pickings.id,
            }

        action = self.env.ref('stock.stock_picking_action_picking_type').read()[0]
        action['domain'] = [('id', 'in', pickings.ids)]
        return action

    #Create consignment picking for KGNCP
    def _create_consignment_picking(self):
        StockPicking = self.env['stock.picking']

        kg_hcm_location = self.env['stock.location'].search([
            ('complete_name', 'like', '%KGNCP/Tồn kho%')
        ], limit=1)
        if not kg_hcm_location:
            raise UserError("Không tìm thấy địa điểm 'KGNCP/Tồn kho' trong hệ thống.")

        warehouse = self.env['stock.warehouse'].search([
            ('view_location_id', 'parent_of', kg_hcm_location.id)
        ], limit=1)

        if not warehouse:
            raise UserError(f"Không tìm thấy kho ứng với địa điểm '{kg_hcm_location.name}'.")

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'),
            ('warehouse_id', '=', warehouse.id),
            ('default_location_dest_id', '=', kg_hcm_location.id)
        ], limit=1)
        if not picking_type:
            raise UserError(f"Không tìm thấy quy trình nhập kho cho {warehouse.name}")

        picking_vals = {
            'partner_id': self.partner_id.id,
            'owner_id': self.partner_id.id,
            'origin': self.name,
            'is_consignment': True,
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': kg_hcm_location.id,
            'move_ids_without_package': []
        }

        # Gộp trước tránh lỗi mất move.line
        move_dict = {}
        for line in self.order_line.filtered(lambda l: not l.display_type):
            key = (line.product_id.id, line.product_uom.id, line.consignment_packed_type, line.unit_of_measure)
            if key in move_dict:
                move_dict[key]['product_uom_qty'] += line.product_uom_qty
            else:
                move_dict[key] = {
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'consignment_packed_type': line.consignment_packed_type,
                    'unit_of_measure': line.unit_of_measure,
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': kg_hcm_location.id,
                }

        for move in move_dict.values():
            picking_vals['move_ids_without_package'].append((0, 0, move))

        picking = StockPicking.create(picking_vals)

        picking.action_confirm()

        return picking

    def _create_consignment_outgoing_picking(self):
        StockPicking = self.env['stock.picking']

        # Tạo dữ liệu cho picking xuất
        picking_vals = {
            'partner_id': self.partner_id.id,
            'owner_id': self.partner_id.id,
            'origin': self.name,
            'is_consignment': True,
            'picking_type_id': self.env['stock.picking.type'].sudo().search([('code', '=', 'outgoing'), ('company_id', '=', 2)], limit=1).id,
            'company_id': 2,
            'location_id': self.env['stock.warehouse'].sudo().search([('company_id', '=', 2)], limit=1).lot_stock_id.id,
            'location_dest_id': self.env['stock.picking.type'].sudo().search([('code', '=', 'outgoing'), ('company_id', '=', 2)], limit=1).default_location_dest_id.id,
            'move_ids_without_package': []
        }

        # Lấy dữ liệu từ incoming picking
        incoming_picking = StockPicking.sudo().search([('origin', '=', self.name), ('state', '=', 'done'), ('is_consignment', '=', True)], limit=1)

        for move in incoming_picking.move_ids:
            qty_needed = sum(move.move_line_ids.mapped("qty_done"))
            move_vals = {
                'name': move.name,
                'product_id': move.product_id.id,
                'product_uom_qty': qty_needed,
                'product_uom': move.product_uom.id,
                'location_id': picking_vals['location_id'],
                'location_dest_id': picking_vals['location_dest_id'],
                'consignment_packed_type': move.consignment_packed_type,
                'unit_of_measure': move.unit_of_measure
            }
            picking_vals['move_ids_without_package'].append((0, 0, move_vals))

        # Tạo và chạy picking
        outgoing_picking = StockPicking.sudo().create(picking_vals)
        outgoing_picking.sudo().action_confirm()
        outgoing_picking.sudo().action_assign()

        return outgoing_picking

    def action_create_outgoing_picking(self):
        self.ensure_one()
        self._create_consignment_outgoing_picking()
    
    # Compute number of pickings with origin sale order
    def _compute_sale_id_stock_picking_count(self):
        for order in self:
            order.sale_id_stock_picking_count = self.env['stock.picking'].search_count([
                ('origin', '=', order.name),
                ('picking_type_id.code', '=', 'incoming')
            ])

    def _compute_sale_id_stock_picking_delivery_count(self):
        for order in self:
            order.sale_id_stock_picking_delivery_count = self.env['stock.picking'].search_count([
                ('origin', '=', order.name),
                ('picking_type_id.code', '=', 'outgoing')
            ])

    def _action_launch_procurement_rule(self, force_company=False):
        """Ghi đè để ngăn tạo phiếu xuất kho nếu là đơn ký gửi"""
        orders = self.filtered(lambda order: not order.is_consignment_order)
        if not orders:
            return
        return super(ConsignmentOrder, orders)._action_launch_procurement_rule(force_company=force_company)
    
    # Bỏ qua quyền multi-company
    @api.model
    def _filter_access_rules(self, operation):
        """Ghi đè quyền truy cập để đơn hàng ký gửi có thể xem ở mọi công ty"""
        if self.is_consignment_order:
            return self.browse([])
        return super()._filter_access_rules(operation)

    def action_view_invoice(self, invoices=False):
        """Override để đảm bảo đơn ký gửi mở form consignment invoice"""
        action = super(ConsignmentOrder, self).action_view_invoice(invoices=invoices)
        print("\n\033[94m[DEBUG] Hàm action_view_invoice được gọi.\033[0m")
        print(">>> invoices:", invoices)
        print(">>> is_consignment_order:", self.is_consignment_order)
        print(">>> Action từ super:", action)
        
        if self.name and 'HDKG' in self.name:
            consignment_view_id = self.env.ref('consignment.consignment_invoice_form_view').id
            print(">>> Hóa đơn có HDKG, view consignment sẽ được dùng.")
    


        if self.is_consignment_order and isinstance(action, dict):
            print("\033[93m[DEBUG] Là đơn consignment và action là dict. Tiếp tục xử lý view...\033[0m")
            consignment_view_id = self.env.ref('consignment.consignment_invoice_form_view').id
            print(">>> View ID đặc biệt (consignment):", consignment_view_id)

            # Kiểm tra nếu action đang mở form view, thì thay đổi nó
            if 'views' in action:
                print("\033[96m[DEBUG] 'views' tồn tại trong action. Đang cập nhật views...\033[0m")
                action['views'] = [(consignment_view_id, 'form')] + [
                    view for view in action['views'] if view[1] != 'form'
                ]
                # Bổ sung context để đánh dấu đây là consignment invoice
                context = action.get('context', {})
                if isinstance(context, str):
                    context = safe_eval(context)
                context['default_is_consignment_invoice'] = True
                action['context'] = context
    
                print(">>> Đây là đơn consignment. Form view đặc biệt sẽ được sử dụng.")
            else:
                action['view_id'] = consignment_view_id
                # Bổ sung context để đánh dấu đây là consignment invoice
                context = action.get('context', {})
                print(">>> Context ban đầu:", context)
                if isinstance(context, str):
                    print("\033[91m[DEBUG] Context là chuỗi. Đang eval...\033[0m")
                    context = safe_eval(context)
                context['default_is_consignment_invoice'] = True
                action['context'] = context
                print(">>> Context sau cập nhật:", context)
                
    
                print("\033[92m[DEBUG] Form view consignment đã được thiết lập thành công.\033[0m")



        return action

    @api.depends_context('lang')
    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id')
    def _compute_tax_totals(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)

            base_lines = []
            for line in order_lines:
                base_line = line._prepare_base_line_for_taxes_computation()

                # Nếu là hàng ký gửi, dùng billing_qty thay vì product_uom_qty
                if order.is_consignment_order:
                    base_line['quantity'] = line.billing_qty
                else:
                    base_line['quantity'] = line.product_uom_qty

                base_lines.append(base_line)

            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)

            order.tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )

    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id')
    def _compute_amounts(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)

            base_lines = []
            for line in order_lines:
                base_line = line._prepare_base_line_for_taxes_computation()

                # Nếu là đơn hàng ký gửi, dùng billing_qty thay vì product_uom_qty
                if order.is_consignment_order:
                    base_line['quantity'] = line.billing_qty
                else:
                    base_line['quantity'] = line.product_uom_qty

                base_lines.append(base_line)

            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)

            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )

            order.amount_untaxed = tax_totals['base_amount_currency']
            order.amount_tax = tax_totals['tax_amount_currency']
            order.amount_total = tax_totals['total_amount_currency']