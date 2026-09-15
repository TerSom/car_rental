from odoo import models, fields

class CarRentalcategory(models.Model):
    _name = 'car.rental.category'
    _description = 'Kategory Mobil'
    _order = 'name asc'

    name = fields.Char(string='Nama Kategory', required=True)
    description = fields.Text(string='Deskripsi')
