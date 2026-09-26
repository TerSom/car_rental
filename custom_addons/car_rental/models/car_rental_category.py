from odoo import models, fields

class CarRentalcategory(models.Model):
    _name = 'car.rental.category'
    _description = 'Vehicle Category'
    _order = 'name asc'

    name = fields.Char(string='Category Name', required=True)
    description = fields.Text(string='Description')
