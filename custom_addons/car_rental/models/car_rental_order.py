from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CarRentalOrder(models.Model):
    _name = 'car.rental.order'
    _description = 'Transaksi rental Mobil'
    _rec_name = 'name'

    name = fields.Char(string='Nomor Sewa', required=True, copy=False, default='new')
    partner_id = fields.Many2one('res.partner',string='Customer', required=True)
    vehicle_id = fields.Many2one('car.rental.vehicle', string='Mobil',required=True)
    date_start = fields.Date(string='Waktu mulai', required=True)
    date_end = fields.Date(string='Waktu selesai', required=True)
    total_days = fields.Integer(string='Total Hari', compute="_compute_total_days", store=True)
    total_amount = fields.Float(string='Total Amount', compute="_compute_total_amount", store=True)
    state = fields.Selection([
        ('draft','Draft'),
        ('confirmed','Dikonfirmasi'),
        ('done', 'selesai'),
        ('cancelled','Batal')
    ],required=True, string='Status', default='draft')
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

    @api.constrains('vehicle_id.state')
    def _check_available(self):
        for order in self:
            if order.vehicle_id.state == 'maintenance':
                raise ValidationError('mobil sedang maintenance tidak bisa')