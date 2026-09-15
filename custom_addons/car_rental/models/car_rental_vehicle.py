from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CarRentalVehicle(models.Model):
    _name = 'car.rental.vehicle'
    _description = 'Rental Mobil'
    _rec_name = 'license_plate'

    license_plate = fields.Char(string='Plat Nomer',required=True)
    brand = fields.Char(string='Merk',required=True)
    model_name = fields.Char(string='Model',required=True)
    category_id = fields.Many2one('car.rental.category', string='Kategory')
    daily_rate = fields.Float(string='Tarif Harian')
    state = fields.Selection([
        ('available','Tersedia'),
        ('rented','Disewa'),
        ('maintenance','Maintenance')
    ], string='Status',default='available',required=True)
    active = fields.Boolean(default=True)
    plate_expiry_date = fields.Date(string='Plate Kadaluarsa')
    is_available = fields.Boolean(compute='_compute_is_available' ,store=True)

    @api.constrains('plate_expiry_date','state')
    def _check_expiry_plate(self):
        today = fields.Date.today()
        for vehicle in self:
            if vehicle.state == 'available' and vehicle.plate_expiry_date and vehicle.plate_expiry_date <= today:
                raise ValidationError('plate nomer sudah kadaluarsa')

    @api.depends('state')
    def _compute_is_available(self):
        for vehicle in self:
            vehicle.is_available = vehicle.state == 'available'
