from odoo import models, fields

class CarRentalFeature(models.Model):
    _name = 'car.rental.feature'
    _description = 'Vehicle Feature'

    name = fields.Char(string='Feature Name', required=True)
    description = fields.Char(string='Description')
    color = fields.Integer(string='Color')
