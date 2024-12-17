# Part of Odoo. See LICENSE file for full copyright and licensing details.
from xmlrpc.client import FastParser

from odoo import api, exceptions, models
from odoo.addons.phone_validation.tools import phone_validation

class BaseModel(models.AbstractModel):
    _inherit = 'base'

    def _phone_format_number(self, number, country, force_format='E164', raise_exception=False):
        """ Format and return number according to the asked format. This is
        mainly a small helper around 'phone_validation.phone_format'."""
        if not number:
            return False

        try:
            number = phone_validation.phone_format(
                number,
                country.code if 'code' in country else False,
                country.phone_code if 'phone_code' in country else False,
                force_format=force_format,
                raise_exception=True,  # do not get original number returned
            )
        except exceptions.UserError:
            if raise_exception:
                raise
            number = False
        return number