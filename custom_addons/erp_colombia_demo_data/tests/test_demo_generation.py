# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestDemoGeneration(TransactionCase):
    """Corre un lote DEMO diminuto (más pequeño que SMALL) para verificar
    que el motor completo funciona sin necesidad de esperar un SMALL real."""

    def test_tiny_batch_generates_and_validates(self):
        batch = self.env['erp.colombia.demo.batch'].create({
            'mode': 'custom',
            'seed': 42,
            'n_clientes': 5,
            'n_proveedores': 3,
            'n_empresas': 2,
            'n_productos': 6,
            'n_categorias': 3,
            'n_bodegas': 1,
            'n_cotizaciones': 8,
            'n_pedidos': 6,
            'n_ordenes_compra': 6,
            'n_notas_credito': 2,
            'n_pagos_recibidos': 4,
            'n_pagos_realizados': 4,
            'dian_sample_size': 1,
        })
        batch.button_generate()

        self.assertEqual(batch.state, 'done', batch.error_message)
        self.assertEqual(batch.created_clientes, 5)
        self.assertEqual(batch.created_proveedores, 3)
        self.assertEqual(batch.created_productos, 6)
        self.assertTrue(batch.validation_ok, batch.validation_report)

        for partner in batch.partner_ids:
            self.assertTrue(partner.name.startswith('[DEMO]'))
