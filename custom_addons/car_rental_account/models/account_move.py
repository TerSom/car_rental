from odoo import models,fields,api

class AccountMove(models.Model):
    _inherit = 'account.move'

    car_rental_order_id = fields.Many2one('car.rental.order', string='Rental Order')

    def action_view_order(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_window',
            'res_model':'car.rental.order',
            'view_mode':'form',
            'res_id':self.car_rental_order_id.id
        }