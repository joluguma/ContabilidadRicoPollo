# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import ValidationError

# Serie de primos asignada por la DIAN (Orden Administrativa 04 de 1989),
# de derecha a izquierda, para el algoritmo módulo 11 del NIT.
L10N_CO_NIT_WEIGHTS = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]


def l10n_co_compute_verification_digit(nit):
    """Dígito de verificación (módulo 11) para un NIT sin puntos ni guion."""
    digits = [int(d) for d in reversed(nit)]
    total = sum(digit * weight for digit, weight in zip(digits, L10N_CO_NIT_WEIGHTS))
    remainder = total % 11
    return remainder if remainder in (0, 1) else 11 - remainder


class ResPartner(models.Model):
    _inherit = 'res.partner'

    trade_name = fields.Char(string='Nombre comercial')
    l10n_co_verification_digit = fields.Char(
        string='DV', compute='_compute_l10n_co_verification_digit', store=True)

    def _l10n_co_is_nit(self):
        self.ensure_one()
        nit_type = self.env.ref('l10n_co.rut', raise_if_not_found=False)
        return bool(
            nit_type
            and self.country_id.code == 'CO'
            and self.l10n_latam_identification_type_id == nit_type
        )

    @api.depends('vat', 'country_id', 'l10n_latam_identification_type_id')
    def _compute_l10n_co_verification_digit(self):
        for partner in self:
            nit = (partner.vat or '').split('-')[0].strip()
            if partner._l10n_co_is_nit() and nit.isdigit():
                partner.l10n_co_verification_digit = str(
                    l10n_co_compute_verification_digit(nit))
            else:
                partner.l10n_co_verification_digit = False

    @api.constrains('vat', 'country_id', 'l10n_latam_identification_type_id')
    def _check_l10n_co_vat_verification_digit(self):
        for partner in self:
            if not partner._l10n_co_is_nit() or not partner.vat or '-' not in partner.vat:
                continue
            nit, typed_dv = (part.strip() for part in partner.vat.split('-', 1))
            if not nit.isdigit() or not typed_dv.isdigit():
                continue
            expected_dv = l10n_co_compute_verification_digit(nit)
            if int(typed_dv) != expected_dv:
                raise ValidationError(self.env._(
                    'El dígito de verificación del NIT %(nit)s no es válido: '
                    'ingresaste %(typed)s, el correcto es %(expected)s.',
                    nit=nit, typed=typed_dv, expected=expected_dv,
                ))
