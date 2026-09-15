from odoo import models, fields, api

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