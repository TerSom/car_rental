from odoo import models,fields,api
from odoo.exceptions import ValidationError

class CarRentalReturnWizard(models.TransientModel):
    _name = 'car.rental.return.wizard'
    _description = 'Vehicle Return Wizard'

    order_id = fields.Many2one('car.rental.order', string='Order', required=True)
    vehicle_id = fields.Many2one('car.rental.vehicle', string='Vehicle')
    actual_return_date = fields.Date(string='Actual Return Date', default=fields.Date.today(), required=True)
    milage_return = fields.Integer(string='Current Mileage', required=True)
    condition_notes = fields.Text(string='Vehicle Condition Notes')

    def action_confirm_return(self):
        self.ensure_one()
        for wizard in self:
            if wizard.actual_return_date <= self.order_id.date_start:
                raise ValidationError("Return date must be after the rental start date.")
            if wizard.milage_return <= self.vehicle_id.milage:
                raise ValidationError("Current mileage must be greater than previous mileage.")

            wizard.order_id.state = 'done'
            wizard.order_id.vehicle_id.state = 'available'
            wizard.vehicle_id.milage = wizard.milage_return
            wizard.order_id.message_post(body='Vehicle has been returned.')