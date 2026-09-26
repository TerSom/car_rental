import io
import base64
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CarRentalExportWizard(models.TransientModel):
    _name = 'car.rental.export.wizard'
    _description = 'Export Car Rental Excel Wizard'

    date_from = fields.Date(string='Start Date', required=True)
    date_to = fields.Date(string='End Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status')
    xlsx_file = fields.Binary(string='Excel File', readonly=True)
    file_name = fields.Char(string='File Name', readonly=True)
    only_overdue = fields.Boolean(string='Only Overdue')

    def action_generate_xlsx(self):
        today = fields.Date.today()
        self.ensure_one()
        domain = []
        if self.date_from:
            domain.append(('date_start', '>=', self.date_from))
        if self.date_to:
            domain.append(('date_start', '<=', self.date_to))
        if self.state:
            domain.append(('state', '=', self.state))
        if self.only_overdue:
            domain.append(('date_end', '<', today)),
            domain.append(('state', '=', 'confirmed'))

        if self.date_from >= self.date_to:
            raise ValidationError('Start date must be before end date.')

        orders = self.env['car.rental.order'].search(domain)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Rental Orders')

        headers = ['Order Number', 'Customer', 'Vehicle', 'Start Date', 'End Date', 'Total Days', 'Total Amount', 'Status']
        for col, header in enumerate(headers):
            sheet.write(0, col, header)

        for row, order in enumerate(orders, start=1):
            sheet.write(row, 0, order.name)
            sheet.write(row, 1, order.partner_id.name)
            sheet.write(row, 2, order.vehicle_id.license_plate)
            sheet.write(row, 3, str(order.date_start))
            sheet.write(row, 4, str(order.date_end))
            sheet.write(row, 5, order.total_days)
            sheet.write(row, 6, order.total_amount)
            sheet.write(row, 7, order.state)

        workbook.close()
        output.seek(0)

        self.xlsx_file = base64.b64encode(output.read())
        self.file_name = 'car_rental_report.xlsx'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'car.rental.export.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }