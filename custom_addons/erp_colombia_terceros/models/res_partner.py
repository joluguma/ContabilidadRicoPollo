# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
import logging

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

# Servicio interno (no documentado oficialmente, pero es el mismo que usa
# https://ruesfront.rues.org.co) del Registro Único Empresarial y Social
# (RUES) de Confecámaras. Requiere encabezados Origin/Referer de un
# navegador real o responde 403 — no requiere autenticación ni tiene
# costo. Al ser un servicio interno sin documentación pública ni
# garantía contractual de estabilidad, cualquier llamada debe fallar en
# silencio (nunca bloquear la creación/edición del tercero): si un día
# deja de responder, el usuario simplemente completa los datos a mano
# como lo hacía antes de esta integración.
RUES_SEARCH_URL = 'https://elasticprd.rues.org.co/api/ConsultasRUES/BusquedaAvanzadaRM'
RUES_DETAIL_URL = 'https://ruesapi.rues.org.co/WEB2/api/Expediente/DetalleRM/{id_rm}'
RUES_HEADERS = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Origin': 'https://ruesfront.rues.org.co',
    'Referer': 'https://ruesfront.rues.org.co/',
}
RUES_TIMEOUT = 8
# Timeout más corto para el intento AUTOMÁTICO al escribir solo números en
# un campo Cliente/Proveedor (name_create): la mayoría de esos casos son
# cédulas de persona que RUES no tiene, así que debe fallar rápido para no
# sentirse lento en el caso más común, en vez de esperar los 8s completos.
RUES_AUTO_TIMEOUT = 4

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

    @api.model
    def _rues_autofill_vals(self, name_value, timeout=RUES_AUTO_TIMEOUT):
        """Si `name_value` son solo dígitos con pinta de NIT/cédula,
        intenta RUES y devuelve un dict de valores a aplicar (nombre
        real, vat, tipo, dirección…), o None si no aplica o no se
        encontró nada (RUES no cubre cédulas de la mayoría de personas
        naturales — solo comerciantes registrados)."""
        stripped = (name_value or '').strip()
        if not (stripped.isdigit() and 6 <= len(stripped) <= 10):
            return None
        data = self._rues_fetch(stripped, timeout=timeout)
        if not data or not data.get('razon_social'):
            return None
        vals = self._rues_values_from_detail(data)
        vals['is_company'] = not self._rues_is_natural_person(data)
        dv = (data.get('dv') or '').strip()
        vals['vat'] = f'{stripped}-{dv}' if dv else stripped
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        """Cubre TODOS los caminos de creación con solo números como
        nombre: el "Crear X" de un clic (que internamente llama a
        name_create -> create), el diálogo "Crear y editar..." (que
        llama a create directo con lo que se haya escrito en el
        formulario) y creaciones programáticas/importaciones."""
        for vals in vals_list:
            if vals.get('name') and not vals.get('vat'):
                extra = self._rues_autofill_vals(vals['name'])
                if extra:
                    vals.update(extra)
        return super().create(vals_list)

    def write(self, vals):
        """Cubre el caso de editar el Nombre de un contacto YA
        existente y dejarlo en puros números (ej. corrigiendo a mano un
        NIT que quedó mal la primera vez) — solo si ese contacto no
        tenía ya una identificación cargada, para no reinterpretar el
        nombre de un contacto real que simplemente empieza con dígitos."""
        if len(self) == 1 and vals.get('name') and not vals.get('vat') and not self.vat:
            extra = self._rues_autofill_vals(vals['name'])
            if extra:
                vals = dict(vals, **extra)
        return super().write(vals)

    def action_rues_lookup(self):
        """Autocompleta razón social/nombre, dirección y contacto desde
        el Registro Único Empresarial y Social (RUES) a partir del NIT
        ya escrito en el formulario. RUES cubre tanto empresas (SAS,
        LTDA, etc.) como personas naturales registradas como
        comerciantes — en ambos casos ajusta "¿Empresa?" según lo que
        RUES reporte, no según lo que estaba marcado antes."""
        self.ensure_one()
        nit = (self.vat or '').split('-')[0].strip()
        if not nit.isdigit():
            raise UserError(_('Escribe primero un NIT válido (solo números) en "Número de Identificación".'))

        data = self._rues_fetch(nit)
        if not data:
            raise UserError(_(
                'No se encontró el NIT %(nit)s en RUES, o el servicio no '
                'respondió. Puedes completar los datos manualmente.',
                nit=nit,
            ))

        vals = self._rues_values_from_detail(data)
        vals['is_company'] = not self._rues_is_natural_person(data)
        self.write(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('RUES'),
                'message': _('Datos actualizados desde RUES: %s', data.get('razon_social') or ''),
                'type': 'success',
            },
        }

    def _rues_fetch(self, nit, timeout=RUES_TIMEOUT):
        """Devuelve el detalle completo de RUES para un NIT, o False si
        no se encuentra o el servicio falla (nunca lanza una excepción
        de red hacia el usuario).

        OJO: la búsqueda de RUES no es de coincidencia exacta — para
        "10750902" llegó a devolver el registro de "107509022" (el NIT
        buscado es un prefijo del encontrado). Por eso se descarta
        cualquier resultado cuyo nit no sea idéntico al buscado, para no
        pegarle a un contacto los datos de otra persona/empresa."""
        try:
            search_resp = requests.post(
                RUES_SEARCH_URL, json={'nit': nit},
                headers=RUES_HEADERS, timeout=timeout,
            )
            search_resp.raise_for_status()
            registros = (search_resp.json() or {}).get('registros') or []
            match = next(
                (r for r in registros if str(r.get('nit', '')).strip() == nit),
                None,
            )
            if not match or not match.get('id_rm'):
                return False

            detail_resp = requests.get(
                RUES_DETAIL_URL.format(id_rm=match['id_rm']),
                headers=RUES_HEADERS, timeout=timeout,
            )
            detail_resp.raise_for_status()
            return (detail_resp.json() or {}).get('registros') or False
        except (requests.RequestException, ValueError) as exc:
            _logger.warning('RUES no disponible para NIT %s: %s', nit, exc)
            return False

    def _rues_is_natural_person(self, data):
        """RUES también registra personas naturales comerciantes (no
        solo sociedades) — en ese caso el contacto debe quedar marcado
        como Persona, no Empresa, aunque tenga NIT."""
        return 'PERSONA NATURAL' in (data.get('organizacion_juridica') or '').upper()

    def _rues_values_from_detail(self, data):
        vals = {}
        if data.get('razon_social'):
            vals['name'] = data['razon_social']
        street = data.get('dir_comercial') or data.get('dir_fiscal')
        if street:
            vals['street'] = street
        email = data.get('email_com') or data.get('email_fiscal')
        if email:
            vals['email'] = email
        phone = data.get('tel_com_1') or data.get('tel_fiscal_1')
        if phone:
            vals['phone'] = phone
        mun_code = (data.get('mun_comercial') or data.get('mun_fiscal') or '').strip()
        if mun_code.isdigit():
            city = self.env['res.city'].search([('zipcode', '=', mun_code.zfill(5))], limit=1)
            if city:
                vals['city_id'] = city.id
                vals['city'] = city.name
                vals['state_id'] = city.state_id.id
        return vals
