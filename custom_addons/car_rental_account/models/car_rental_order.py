from odoo import models,fields,api,Command
from odoo.exceptions import UserError

class CarRentalOrder(models.Model):
    _inherit = 'car.rental.order'

    invoice_ids = fields.One2many('account.move', 'car_rental_order_id', string='Invoice')
    invoice_count = fields.Integer(compute='_compute_invoice_count')
    payment_state = fields.Selection(
        related='invoice_ids.payment_state',
        string='Status Pembayaran',
    )

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for order in self:
            order.invoice_count = len(order.invoice_ids)

    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_ids:
            raise UserError('Order ini sudah punya invoice')
        invoice_vals = {
            'move_type':'out_invoice',
            'partner_id': self.partner_id.id,
            'car_rental_order_id': self.id,
            'invoice_line_ids': [
                Command.create({
                    'name': f'Sewa Moil {self.vehicle_id.license_plate} ({self.date_start}) - ({self.date_end})',
                    'quantity': 1,
                    'price_unit': self.total_amount
                })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        return{
            'type':'ir.actions.act_window',
            'res_model':'account.move',
            'view_mode':'form',
            'res_id': invoice.id,
        }
    
    def aciton_view_invoices(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_window',
            'res_model':'account.move',
            'view_mode':'form',
            'domain': [('id','in',self.invoice_ids.ids)],
            'res_id':self.invoice_ids.id
        }
