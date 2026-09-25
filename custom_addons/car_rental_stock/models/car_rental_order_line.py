from odoo import models, fields


class CarRentalOrderLine(models.Model):
    _name = 'car.rental.order.line'
    _description = 'Rental Order Accessory Line'

    order_id = fields.Many2one(
        'car.rental.order', string='Order', ondelete='cascade', required=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Aksesoris',
        required=True,
        domain=[('is_storable', '=', True)],
    )
    qty = fields.Float(string='Jumlah', default=1.0, required=True)
    product_uom_id = fields.Many2one(
        related='product_id.uom_id', string='Satuan', readonly=True
    )
