# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
{
    'name': 'ERP Colombia - Terceros',
    'version': '19.0.1.0.0',
    'category': 'ERP Colombia',
    'summary': 'Dígito de verificación del NIT y nombre comercial sobre Contactos',
    'description': """
ERP Colombia - Terceros
=========================

Extiende `res.partner` (no lo duplica) para cubrir dos huecos que ni el
core de Odoo ni la localización OCA de Colombia resuelven todavía:

* **Dígito de verificación (DV) del NIT**: se calcula automáticamente
  con el algoritmo módulo 11 de la DIAN (Orden Administrativa 04 de
  1989) y se valida si el usuario lo escribe a mano en el VAT
  (ej. "900197268-4").
* **Nombre comercial**: campo separado de la razón social (`name`).

No se toca el modelo de contactos: todo es herencia (`_inherit`).
""",
    'author': 'ERP Colombia',
    'license': 'LGPL-3',
    'depends': ['contacts', 'l10n_co'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
}
