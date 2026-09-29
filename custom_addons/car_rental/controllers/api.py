import json

from odoo import http
from odoo.exceptions import AccessError,UserError,ValidationError
from odoo.http import Response, request

WRITABLE_FIELD = [
    'license_plate', 'brand', 'model_name',
    'category_id', 'daily_rate', 'plate_expiry_date',
]
REQUIRED_FIELD = ['license_plate']

def _json_response(data,status=200):
    return Response(
        json.dumps(data, default=str),
        status=status,
        content_type='application/json'
    )

def _get_json_body():
    try:
        body = json.loads(request.httprequest.data or b'{}')
    except ValueError:
        return None
    return body if isinstance(body, dict) else None

def _serialize_vehicle(vehicle):
    return{
        'id': vehicle.id,
        'license_plate': vehicle.license_plate,
        'brand': vehicle.brand or None,
        'model_name': vehicle.model_name or None,
        'category': {
            'id': vehicle.category_id.id,
            'name': vehicle.category_id.name,
        } if vehicle.category_id else None,
        'daily_rate': vehicle.daily_rate,
        'state': vehicle.state,
        'plate_expiry_date': vehicle.plate_expiry_date or None,
    }

class CarRentalApi(http.Controller):

    # Read(List)
    @http.route('/api/car_rental/vehicles', type='http', auth='user', methods=['GET'])
    def list_vehicles(self, state=None, limit=20, offset=0, **kwargs):
        try:
            limit = min(int(limit), 100)
            offset = int(offset)
        except ValueError:
            return _json_response({'error': 'limit dan offset harus angka'}, status=400)
        
        domain = [('state','=',state)] if state else []
        vehicle = request.env['car.rental.vehicle']
        vehicles = vehicle.search(domain, limit=limit, offset=offset, order='id')
        return _json_response({
            'count': vehicle.search_count(domain),
            'results': [_serialize_vehicle(v) for v in vehicles]
        })

    # Read From id
    @http.route('/api/car_rental/vehicles/<int:vehicle_id>',type='http', auth='user',methods=['GET'])
    def get_vehicle(self, vehicle_id, **kwargs):
        vehicle = request.env['car.rental.vehicle'].browse(vehicle_id).exists()
        if not vehicle:
            return _json_response({'error': 'Vehicle tidak ditemukan'}, status=400)
        return _json_response(_serialize_vehicle(vehicle))

    # Create
    @http.route('/api/car_rental/vehicles', type='http', auth='user', methods=['POST'], csrf=False)
    def create_vehicle(self, **kwargs):
        body = _get_json_body()
        if body is None:
            return _json_response({'error': 'Body harus berupa JSON object'}, status=400)

        vals = {k: v for k, v in body.items() if k in WRITABLE_FIELD}
        mising = [f for f in REQUIRED_FIELD if not vals.get(f)]
        if mising:
            return _json_response({'error':'Field wajib diisi: ' + ','.join(mising)}, status=400)
        
        try:
            with request.env.cr.savepoint():
                vehicle = request.env['car.rental.vehicle'].create(vals)
        except AccessError as e:
            return _json_response({'error': str(e)}, status=403)
        except (ValidationError, UserError) as e:
            return _json_response({'error': str(e)}, status=400)
        return _json_response(_serialize_vehicle(vehicle), status=201)

    @http.route('/api/car_rental/vehicles/<int:vehicle_id>',type='http',auth='user',methods=['DELETE'],csrf=False)
    def delete_vehicle(self, vehicle_id, **kwargs):
        vehicle = request.env['car.rental.vehicle'].browse(vehicle_id).exists()
        if not vehicle:
            return _json_response({'error': 'Vehicle tidak ditemukan'}, status=404)

        try:
            with request.env.cr.savepoint():
                vehicle.unlink()
        except AccessError as e:
            return _json_response({'error': str(e)}, status=403)
        except (ValidationError, UserError) as e:
            return _json_response({'error': str(e)}, status=400)
        return _json_response({'deleted': True, 'id': vehicle_id})