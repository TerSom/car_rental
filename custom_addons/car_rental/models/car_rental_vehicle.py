from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CarRentalVehicle(models.Model):
    _name = 'car.rental.vehicle'
    _description = 'Rental Vehicle'
    _rec_name = 'license_plate'

    license_plate = fields.Char(string='License Plate', required=True)
    brand = fields.Char(string='Brand', required=True)
    model_name = fields.Char(string='Model', required=True)
    category_id = fields.Many2one('car.rental.category', string='Category')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    daily_rate = fields.Monetary(string='Daily Rate')
    state = fields.Selection([
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Maintenance')
    ], string='Status', default='available', required=True)
    active = fields.Boolean(default=True)
    plate_expiry_date = fields.Date(string='Plate Expiry Date')
    is_available = fields.Boolean(compute='_compute_is_available', store=True)
    order_ids = fields.One2many('car.rental.order', 'vehicle_id', string='Rental History')
    feature_ids = fields.Many2many('car.rental.feature', string='Vehicle Features')
    milage = fields.Integer(string='Mileage', required=True, default=0)

    @api.constrains('plate_expiry_date', 'state')
    def _check_expiry_plate(self):
        today = fields.Date.today()
        for vehicle in self:
            if vehicle.state == 'available' and vehicle.plate_expiry_date and vehicle.plate_expiry_date <= today:
                raise ValidationError('License plate has expired.')

    @api.depends('state')
    def _compute_is_available(self):
        for vehicle in self:
            vehicle.is_available = vehicle.state == 'available'