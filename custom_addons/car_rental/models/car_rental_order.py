from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CarRentalOrder(models.Model):
    _name = 'car.rental.order'
    _description = 'Car Rental Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Rental Number', required=True, copy=False, default='New', readonly=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    vehicle_id = fields.Many2one('car.rental.vehicle', string='Vehicle', required=True, tracking=True)
    date_start = fields.Date(string='Start Date', required=True, default=fields.Date.today, tracking=True)
    date_end = fields.Date(string='End Date', required=True, tracking=True)
    total_days = fields.Integer(string='Total Days', compute="_compute_total_days", store=True)
    total_amount = fields.Float(string='Total Amount', compute="_compute_total_amount", store=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], required=True, string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    reminder_count = fields.Integer(string='Reminder Count', default=0, copy=False)
    vehicle_ids = fields.Many2many(
        'car.rental.vehicle',
        string='Vehicles',
        compute='_compute_vehicle_ids',
    )

    @api.depends('vehicle_id')
    def _compute_vehicle_ids(self):
        for order in self:
            order.vehicle_ids = order.vehicle_id

    @api.depends('date_start','date_end')
    def _compute_total_days(self):
        for order in self:
            if order.date_start and order.date_end:
                delta = (order.date_end - order.date_start).days
                order.total_days = delta if delta > 0 else 0
            else:
                order.total_days = 0

    @api.depends('total_days','vehicle_id.daily_rate')
    def _compute_total_amount(self):
        for order in self:
            order.total_amount = order.vehicle_id.daily_rate * order.total_days

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for order in self:
            if order.date_start and order.date_end and order.date_end <= order.date_start:
                raise ValidationError('End date must be after start date.')

    @api.constrains('vehicle_id')
    def _check_available(self):
        for order in self:
            if order.vehicle_id.state in ['maintenance','rented']:
                raise ValidationError('Vehicle is currently under maintenance or rented.')

    def action_open_return_wizard(self):
        self.ensure_one()
        return {
            'name': 'Return Vehicle',
            'type': 'ir.actions.act_window',
            'res_model': 'car.rental.return.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_vehicle_id': self.vehicle_id.id,
                'default_milage_return': self.vehicle_id.milage,
            }
        }

    def action_confirm(self):
        for order in self:
            order.state = 'confirmed'
            order.vehicle_id.state = 'rented'
            order.message_post(body='Rental confirmed, vehicle ready for delivery/pickup.')

    def action_cancel(self):
        for order in self:
            order.state = 'cancelled'
            order.vehicle_id.state = 'available'
            order.message_post(body='Rental cancelled.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') in ('New', 'new', '/'):
                vals['name'] = self.env['ir.sequence'].next_by_code('car.rental.order') or 'New'

        orders = super().create(vals_list)

        for order in orders:
            order.state = 'confirmed'
            order.vehicle_id.state = 'rented'

        return orders

    @api.model
    def cron_check_overdue_order(self):
        today = fields.Date.today()
        overdue_orders = self.search([
            ('state', '=', 'confirmed'),
            ('date_end', '<', today),
            ('reminder_count', '<', 3),
        ])
        for order in overdue_orders:
            order.reminder_count += 1
            day_late = (today - order.date_end).days

            if order.reminder_count == 1:
                body = f"Order {order.name} is overdue by {day_late} days. Please return the vehicle immediately."
            elif order.reminder_count == 2:
                body = f"Order {order.name} is overdue by {day_late} days. Late fees are accumulating, please return the vehicle promptly."
            elif order.reminder_count == 3:
                body = f"Order {order.name} is overdue by {day_late} days! Vehicle has not been returned. The rental company will take formal action."

            order.message_post(body=body)

