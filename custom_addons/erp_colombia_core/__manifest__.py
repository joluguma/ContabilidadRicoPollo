# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
{
    'name': 'ERP Colombia - Core',
    'version': '19.0.1.0.0',
    'category': 'ERP Colombia',
    'summary': 'Núcleo común de ERP Colombia: menú raíz y auditoría transversal',
    'description': """
ERP Colombia - Core
====================

Módulo núcleo del proyecto ERP Colombia. No contiene lógica de negocio
de inventario, contabilidad ni DIAN: únicamente provee lo que los demás
módulos erp_colombia_* necesitan en común:

* Menú raíz de la aplicación "ERP Colombia".
* Grupos de seguridad base (Administrador, Auditor) del proyecto.
* Mecanismo de auditoría transversal (`erp.colombia.audit.mixin`) que
  otros módulos heredan para registrar creación, eliminación y cambios
  de estado de documentos críticos (facturas, notas, comprobantes,
  ajustes de inventario, configuración DIAN).
""",
    'author': 'ERP Colombia',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/erp_colombia_security.xml',
        'security/ir.model.access.csv',
        'views/erp_colombia_menus.xml',
        'views/erp_colombia_audit_views.xml',
    ],
    'application': True,
    'sequence': 1,
    'installable': True,
}
