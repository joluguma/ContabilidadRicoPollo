# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
{
    'name': 'ERP Colombia - Reportes',
    'version': '19.0.1.0.0',
    'category': 'ERP Colombia',
    'summary': 'Kardex de inventario en el formato clásico colombiano',
    'description': """
ERP Colombia - Reportes
=========================

Odoo (ni Community ni la localización OCA de Colombia) trae un reporte
de Kardex con el formato clásico usado en Colombia (fecha, documento,
tipo de movimiento, entrada, salida, saldo, costo unitario, costo total,
bodega, producto). Los datos ya existen en `stock.move` (con los campos
`value`/`is_in`/`is_out` que trae `stock_account`); este módulo solo
añade el asistente que los presenta en ese formato, con exportación a
Excel.

No reimplementa el motor de inventario ni de valorización: se apoya
enteramente en `stock_account`.
""",
    'author': 'ERP Colombia',
    'license': 'LGPL-3',
    'depends': ['stock_account', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/erp_colombia_kardex_wizard_views.xml',
        'views/erp_colombia_reportes_menus.xml',
    ],
    'installable': True,
}
