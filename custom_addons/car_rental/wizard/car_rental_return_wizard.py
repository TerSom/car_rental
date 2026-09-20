from odoo import models,fields,api
from odoo.exceptions import ValidationError

class CarRentalReturnWizard(models.TransientModel):
    _name = 'car.rental.return.wizard'
    _description = 'Wizard Pengembalian Mobil'

    order_id = fields.Many2one('car.rental.order', string='Order' ,required=True)
    vehicle_id = fields.Many2one('car.rental.vehicle', string='Mobil')
    actual_return_date = fields.Date(string='Tanggal Kembali Aktual', default=fields.Date.today(),required=True)
    milage_return = fields.Integer(string='Kilometer Saat ini',required=True)
    condition_notes = fields.Text(string='Catatan Kondisi Mobil')

    def action_confirm_return(self):
        self.ensure_one()
        for wizard in self:
            if wizard.actual_return_date <= self.order_id.date_start:
                raise ValidationError("Tanggal kembali harus setelah tanggal mulai sewa.")
            if wizard.milage_return <= self.vehicle_id.milage:
                raise ValidationError("Kilometer saat ini harus lebih besar dari kilometer sebelumnya.")

            wizard.order_id.state = 'done'
            wizard.order_id.vehicle_id.state = 'available'
            wizard.vehicle_id.milage = wizard.milage_return