# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
{
    'name': 'ERP Colombia - Seguridad',
    'version': '19.0.1.0.0',
    'category': 'ERP Colombia',
    'summary': 'Perfiles de seguridad colombianos sobre los grupos nativos de Odoo',
    'description': """
ERP Colombia - Seguridad
==========================

No crea permisos nuevos: define 7 perfiles (grupos) que un
administrador puede asignar a un usuario con un solo clic, cada uno
implicando los grupos nativos de Odoo que ya resuelven ese rol.
`Administrador` y `Auditor` ya existían en `erp_colombia_core`; este
módulo agrega los operativos: Contador, Auxiliar contable, Inventario,
Compras, Ventas, Facturación y Consulta.

Vive en un módulo aparte (no en `erp_colombia_core`, que se mantiene
sin dependencias de negocio, ni en `erp_colombia_contabilidad`, que es
solo auditoría) porque necesita depender de `account`, `sale`,
`purchase` y `stock` a la vez.
""",
    'author': 'ERP Colombia',
    'license': 'LGPL-3',
    'depends': ['erp_colombia_core', 'account', 'sale', 'purchase', 'stock'],
    'data': [
        'security/erp_colombia_perfiles.xml',
    ],
    'installable': True,
}
