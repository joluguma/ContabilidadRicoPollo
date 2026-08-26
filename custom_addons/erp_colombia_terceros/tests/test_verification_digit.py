# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged

from ..models.res_partner import l10n_co_compute_verification_digit


@tagged('post_install', '-at_install')
class TestL10nCoVerificationDigit(TransactionCase):

    def setUp(self):
        super().setUp()
        self.co = self.env.ref('base.co')
        self.nit_type = self.env.ref('l10n_co.rut')

    def test_algorithm_known_values(self):
        # Ejemplos verificados con el algoritmo módulo 11 publicado por la DIAN
        # (Orden Administrativa 04 de 1989).
        self.assertEqual(l10n_co_compute_verification_digit('800197268'), 4)
        self.assertEqual(l10n_co_compute_verification_digit('902025831'), 4)

    def test_partner_computes_dv_for_nit(self):
        # Odoo (base_vat) exige el NIT colombiano en formato "NIT-DV";
        # se usa aquí el DV correcto para no chocar con esa validación.
        partner = self.env['res.partner'].create({
            'name': 'Empresa de prueba SAS',
            'is_company': True,
            'country_id': self.co.id,
            'l10n_latam_identification_type_id': self.nit_type.id,
            'vat': '800197268-4',
        })
        self.assertEqual(partner.l10n_co_verification_digit, '4')

    def test_partner_no_dv_for_non_nit(self):
        cedula_type = self.env.ref('l10n_co.national_citizen_id')
        # no_vat_validation: aquí solo interesa el cómputo del DV, no la
        # validación de formato de base_vat (fuera del alcance de este módulo).
        partner = self.env['res.partner'].with_context(no_vat_validation=True).create({
            'name': 'Persona sin NIT',
            'is_company': False,
            'country_id': self.co.id,
            'l10n_latam_identification_type_id': cedula_type.id,
            'vat': '123456789',
        })
        self.assertFalse(partner.l10n_co_verification_digit)

    def test_constraint_rejects_wrong_dv(self):
        with self.assertRaises(ValidationError):
            self.env['res.partner'].create({
                'name': 'Empresa con DV incorrecto',
                'is_company': True,
                'country_id': self.co.id,
                'l10n_latam_identification_type_id': self.nit_type.id,
                'vat': '800197268-9',
            })

    def test_constraint_accepts_correct_dv(self):
        partner = self.env['res.partner'].create({
            'name': 'Empresa con DV correcto',
            'is_company': True,
            'country_id': self.co.id,
            'l10n_latam_identification_type_id': self.nit_type.id,
            'vat': '800197268-4',
        })
        self.assertEqual(partner.l10n_co_verification_digit, '4')
