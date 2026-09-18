from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    driver_license_number = fields.Char(string='Nomor SIM')