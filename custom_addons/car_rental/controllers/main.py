from odoo import http,fields
from odoo.http import request
import json

class CarRentalController(http.Controller):
    @http.route('/car_rental/overdue_count', type='json', auth='user')
    def get_overdue_count(self, **kwargs):
        count = request.env['car.rental.order'].search_count([
            ('state','=','confirmed'),
            ('date_end', '<', fields.Date.today()),
        ])
        return {'overduea_count':count}