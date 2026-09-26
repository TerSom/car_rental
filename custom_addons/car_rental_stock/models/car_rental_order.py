from odoo import models, fields, api, Command
from odoo.exceptions import UserError


class CarRentalOrder(models.Model):
    _inherit = 'car.rental.order'

    addon_line_ids = fields.One2many('car.rental.order.line', 'order_id', string='Accessories')
    picking_ids = fields.One2many('stock.picking', 'car_rental_order_id', string='Transfers')
    picking_count = fields.Integer(string='Transfers', compute='_compute_picking_count')
    has_outgoing_picking = fields.Boolean(string='Accessories Delivered', compute='_compute_picking_status')
    has_incoming_picking = fields.Boolean(string='Accessories Returned', compute='_compute_picking_status')
    is_outgoing_done = fields.Boolean(string='Outgoing Transfer Validated', compute='_compute_picking_status')

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for order in self:
            order.picking_count = len(order.picking_ids)

    @api.depends('picking_ids.state', 'picking_ids.picking_type_code')
    def _compute_picking_status(self):
        for order in self:
            active = order.picking_ids.filtered(lambda p: p.state != 'cancel')
            order.has_outgoing_picking = any(
                p.picking_type_code == 'outgoing' for p in active
            )
            order.has_incoming_picking = any(
                p.picking_type_code == 'incoming' for p in active
            )
            order.is_outgoing_done = any(
                p.picking_type_code == 'outgoing' and p.state == 'done' for p in active
            )

    def _get_warehouse(self):
        self.ensure_one()
        return self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )

    def action_create_outgoing_picking(self):
        self.ensure_one()
        if not self.addon_line_ids:
            raise UserError('No accessories found for this order.')
        if self.has_outgoing_picking:
            raise UserError('Accessories for this order have already been delivered.')

        warehouse = self._get_warehouse()
        picking_type = warehouse.out_type_id
        if not picking_type:
            raise UserError('Delivery order operation type not found.')

        customer_location = (
            self.partner_id.property_stock_customer
            or self.env.ref('stock.stock_location_customers')
        )
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': picking_type.default_location_src_id.id,
            'location_dest_id': customer_location.id,
            'origin': self.name,
            'car_rental_order_id': self.id,
            'move_ids': [
                Command.create({
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': customer_location.id,
                })
                for line in self.addon_line_ids
            ],
        })
        picking.action_confirm()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': picking.id,
        }

    def action_create_incoming_picking(self):
        self.ensure_one()
        if not self.addon_line_ids:
            raise UserError('No accessories found for this order.')
        if not self.has_outgoing_picking:
            raise UserError('Accessories have not been delivered yet.')
        if self.has_incoming_picking:
            raise UserError('Accessories for this order have already been returned.')

        warehouse = self._get_warehouse()
        picking_type = warehouse.in_type_id
        if not picking_type:
            raise UserError('Receipts operation type not found.')

        customer_location = (
            self.partner_id.property_stock_customer
            or self.env.ref('stock.stock_location_customers')
        )
        picking = self.env['stock.picking'].create({
            'partner_id': self.partner_id.id,
            'picking_type_id': picking_type.id,
            'location_id': customer_location.id,
            'location_dest_id': picking_type.default_location_dest_id.id,
            'origin': f"Return {self.name}",
            'car_rental_order_id': self.id,
            'move_ids': [
                Command.create({
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': customer_location.id,
                    'location_dest_id': picking_type.default_location_dest_id.id,
                })
                for line in self.addon_line_ids
            ],
        })
        picking.action_confirm()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': picking.id,
        }

    def action_view_pickings(self):
        self.ensure_one()
        action = {
            'name': 'Transfers',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'context': {'default_car_rental_order_id': self.id},
        }
        if len(self.picking_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.picking_ids.id
        else:
            action['view_mode'] = 'list,form'
            action['domain'] = [('id', 'in', self.picking_ids.ids)]
        return action

