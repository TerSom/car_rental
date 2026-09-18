from odoo import models,fields,api

class CarRentalFeature(models.Model):
    _name = 'car.rental.feature'
    _description = 'Fitur Mobil'

    name = fields.Char(string='Nama Fitur', required=True)
    description = fields.Char(string='Deskripsi')
    color = fields.Integer(string='Warna')
