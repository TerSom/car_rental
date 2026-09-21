from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CarRentalOrder(models.Model):
    _name = 'car.rental.order'
    _description = 'Transaksi rental Mobil'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Nomor Sewa', required=True, copy=False, default='New', readonly=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    vehicle_id = fields.Many2one('car.rental.vehicle', string='Mobil', required=True, tracking=True)
    date_start = fields.Date(string='Waktu mulai', required=True, default=fields.Date.today, tracking=True)
    date_end = fields.Date(string='Waktu selesai', required=True, tracking=True)
    total_days = fields.Integer(string='Total Hari', compute="_compute_total_days", store=True)
    total_amount = fields.Float(string='Total Amount', compute="_compute_total_amount", store=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Dikonfirmasi'),
        ('done', 'selesai'),
        ('cancelled', 'Batal')
    ], required=True, string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Catatan')

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
                raise ValidationError('Tanggal selesai harus setelah tanggal mulai.')

    @api.constrains('vehicle_id')
    def _check_available(self):
        for order in self:
            if order.vehicle_id.state in ['maintenance','rented']:
                raise ValidationError('mobil sedang maintenance atau rented')

    def action_open_return_wizard(self):
        self.ensure_one()
        return{
            'name': 'Pengembalian Mobil',
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
            order.message_post(body='Sewa dikonfimasi, mobil siap di antar')

    def action_cancel(self):
        for order in self:
            order.state = 'cancelled'
            order.vehicle_id.state = 'available'
            order.message_post(body='Sewa Di cancel')

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

