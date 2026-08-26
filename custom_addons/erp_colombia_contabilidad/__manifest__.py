# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
{
    'name': 'ERP Colombia - Contabilidad',
    'version': '19.0.1.0.0',
    'category': 'ERP Colombia',
    'summary': 'Auditoría transversal sobre facturas y comprobantes contables',
    'description': """
ERP Colombia - Contabilidad
=============================

Conecta el mecanismo de auditoría de `erp_colombia_core` a
`account.move` (facturas, notas crédito/débito, comprobantes
contables): registra creación, eliminación, contabilización y
anulación. No crea un motor contable paralelo: usa `account.move` de
Odoo tal cual, solo hereda el mixin de auditoría.

La plantilla de cierre de año fiscal específica del PUC colombiano
(qué cuentas cierran contra cuáles) es una decisión contable pendiente
de definir con el contador de la empresa; el motor que la ejecutará ya
está instalado (`account_fiscal_year_closing`, probado contra el PUC
real en las pruebas integrales).
""",
    'author': 'ERP Colombia',
    'license': 'LGPL-3',
    'depends': ['erp_colombia_core', 'account'],
    'data': [],
    'installable': True,
}
