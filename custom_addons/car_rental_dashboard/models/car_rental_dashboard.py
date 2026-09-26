from datetime import timedelta

from odoo import api, fields, models


class CarRentalDashboard(models.AbstractModel):
    _name = 'car.rental.dashboard'
    _description = 'Car Rental Dashboard'

    @api.model
    def get_dashboard_data(self):
        today = fields.Date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        start_of_month = today.replace(day=1)

        Vehicle = self.env['car.rental.vehicle']
        Order = self.env['car.rental.order']
        Invoice = self.env['account.move']
        Picking = self.env['stock.picking']

        vehicle_states = {
            state: count
            for state, count in Vehicle._read_group([], ['state'], ['__count'])
        }
        order_states = {
            state: count
            for state, count in Order._read_group([], ['state'], ['__count'])
        }

        weekly_orders = Order.search([
            ('date_start', '>=', start_of_week),
            ('date_start', '<=', end_of_week),
            ('state', 'not in', ['cancelled']),
        ])
        revenue_by_day = {
            start_of_week + timedelta(days=offset): 0
            for offset in range(7)
        }
        for order in weekly_orders:
            revenue_by_day[order.date_start] += order.total_amount

        revenue_values = list(revenue_by_day.values())
        revenue_max = max(revenue_values) if any(revenue_values) else 1
        revenue = [
            {
                'label': date.strftime('%a'),
                'amount': amount,
                'height': max(8, round(amount / revenue_max * 100)),
            }
            for date, amount in revenue_by_day.items()
        ]

        overdue_orders = Order.search([
            ('state', '=', 'confirmed'),
            ('date_end', '<', today),
        ], limit=5, order='date_end asc')
        unpaid_invoices = Invoice.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('car_rental_order_id', '!=', False),
        ], limit=5, order='invoice_date_due asc, id desc')
        outgoing_pending = Picking.search([
            ('car_rental_order_id', '!=', False),
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'not in', ['done', 'cancel']),
        ], limit=5, order='scheduled_date asc, id desc')
        incoming_pending = Picking.search([
            ('car_rental_order_id', '!=', False),
            ('picking_type_code', '=', 'incoming'),
            ('state', 'not in', ['done', 'cancel']),
        ], limit=5, order='scheduled_date asc, id desc')

        paid_invoices = Invoice.search_count([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'paid'),
            ('car_rental_order_id', '!=', False),
        ])
        completed_orders = Order.search_count([
            ('state', '=', 'done'),
            ('date_end', '>=', start_of_month),
        ])

        return {
            'today': fields.Date.to_string(today),
            'week_label': '%s - %s' % (
                fields.Date.to_string(start_of_week),
                fields.Date.to_string(end_of_week),
            ),
            'kpis': {
                'vehicles': Vehicle.search_count([]),
                'available_vehicles': vehicle_states.get('available', 0),
                'active_rentals': order_states.get('confirmed', 0),
                'overdue_orders': len(overdue_orders),
                'completed_orders': completed_orders,
                'week_revenue': sum(revenue_values),
            },
            'fleet': {
                'available': vehicle_states.get('available', 0),
                'rented': vehicle_states.get('rented', 0),
                'maintenance': vehicle_states.get('maintenance', 0),
            },
            'payments': {
                'paid': paid_invoices,
                'unpaid': Invoice.search_count([
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', 'in', ['not_paid', 'partial']),
                    ('car_rental_order_id', '!=', False),
                ]),
            },
            'transfers': {
                'outgoing_pending': Picking.search_count([
                    ('car_rental_order_id', '!=', False),
                    ('picking_type_code', '=', 'outgoing'),
                    ('state', 'not in', ['done', 'cancel']),
                ]),
                'incoming_pending': Picking.search_count([
                    ('car_rental_order_id', '!=', False),
                    ('picking_type_code', '=', 'incoming'),
                    ('state', 'not in', ['done', 'cancel']),
                ]),
            },
            'revenue': revenue,
            'alerts': {
                'overdue': [
                    {
                        'id': order.id,
                        'name': order.name,
                        'customer': order.partner_id.name,
                        'vehicle': order.vehicle_id.license_plate,
                        'date': fields.Date.to_string(order.date_end),
                    }
                    for order in overdue_orders
                ],
                'unpaid': [
                    {
                        'id': invoice.id,
                        'name': invoice.name,
                        'customer': invoice.partner_id.name,
                        'amount': invoice.amount_residual,
                    }
                    for invoice in unpaid_invoices
                ],
                'outgoing': [
                    {
                        'id': picking.id,
                        'name': picking.name,
                        'order': picking.car_rental_order_id.name,
                        'customer': picking.partner_id.name,
                    }
                    for picking in outgoing_pending
                ],
                'incoming': [
                    {
                        'id': picking.id,
                        'name': picking.name,
                        'order': picking.car_rental_order_id.name,
                        'customer': picking.partner_id.name,
                    }
                    for picking in incoming_pending
                ],
            },
        }
