from odoo import http
from odoo.http import request

class VehicleController(http.Controller):
    @http.route('/vehicles/search', auth='user', type='json')
    def search_vehicles(self, bien_so_xe=None):
        domain = [('bien_so_xe', 'ilike', bien_so_xe)] if bien_so_xe else []
        vehicles = request.env['vehicle.vehicle'].search(domain)
        return vehicles.read(['ma_so_xe', 'bien_so_xe', 'trang_thai'])