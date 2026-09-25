from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    car_rental_order_id = fields.Many2one('car.rental.order', string='Rental Order')

    def action_view_car_rental_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'car.rental.order',
            'view_mode': 'form',
            'res_id': self.car_rental_order_id.id,
        }
