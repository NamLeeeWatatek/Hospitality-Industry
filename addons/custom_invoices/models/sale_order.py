from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

def action_view_invoice(self, invoices=False):
    # Ghi log để kiểm tra khi hàm được gọi
    print(">>> Hàm action_view_invoice đã được gọi với invoices:", invoices)

    if not invoices:
        invoices = self.mapped('invoice_ids')

    action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')

    # Mặc định: sử dụng form view tiêu chuẩn
    form_view_id = self.env.ref('account.view_move_form').id
    is_consignment = False

    # Kiểm tra xem có dòng nào là consignment_product không
    for line in self.order_line:
        if line.product_template_id.name == 'consignment_product':
            form_view_id = self.env.ref('consignment.consignment_invoice_form_view').id
            is_consignment = True
            break

    if len(invoices) > 1:
        action['domain'] = [('id', 'in', invoices.ids)]
    elif len(invoices) == 1:
        form_view = [(form_view_id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = invoices.id
    else:
        action = {'type': 'ir.actions.act_window_close'}

    # Tạo context mặc định
    context = {
        'default_move_type': 'out_invoice',
    }

    # Nếu là consignment thì thêm context để tạo giá trị mặc định
    if is_consignment:
        context['default_is_consignment_invoice'] = True
        print(">>> Đây là đơn consignment. Form view đặc biệt sẽ được sử dụng.")

    # Thêm thông tin khác nếu chỉ có một record sale.order
    if len(self) == 1:
        context.update({
            'default_partner_id': self.partner_id.id,
            'default_partner_shipping_id': self.partner_shipping_id.id,
            'default_invoice_payment_term_id': self.payment_term_id.id
                or self.partner_id.property_payment_term_id.id
                or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
            'default_invoice_origin': self.name,
        })

    action['context'] = context
    return action
