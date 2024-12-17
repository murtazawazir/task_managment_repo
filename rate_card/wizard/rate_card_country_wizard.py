from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import base64
import pandas as pd


class ImportCountryWizard(models.TransientModel):
    _name = 'rate.card.country.wizard'
    _description = 'Import Countries Wizard'

    attachment = fields.Binary(string="Upload File", required=True)
    file_name = fields.Char(string="File Name")

    def action_import_countries(self):
        if not self.attachment:
            raise ValidationError("Please upload an Excel file.")
        file_data = base64.b64decode(self.attachment)
        try:
            df = pd.read_excel(file_data)
        except Exception as e:
            raise ValidationError(f"Error reading Excel file: {e}")

        country_ids = []
        for country_id in df['country_id']:
            country = self.env['rate.country'].search([('name', '=', country_id)])
            if country:
                country_ids.append(country.id)

        sale_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        if sale_order:
            sale_order.write({'country_ids': [(6, 0, country_ids)]})
