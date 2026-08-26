# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
{
    'name': 'ERP Colombia - Motor de Datos DEMO',
    'version': '19.0.1.0.0',
    'category': 'ERP Colombia',
    'summary': 'Genera datos DEMO reproducibles y relacionados para probar el ERP completo',
    'description': """
ERP Colombia - Motor de Datos DEMO
=====================================

Genera un escenario DEMO completo y coherente (terceros, productos,
inventario, compras, ventas, facturación, pagos, kardex) reutilizando
enteramente el motor de Odoo y los módulos erp_colombia_* — no crea
ningún modelo de negocio nuevo, solo pobla los existentes.

**IMPORTANTE — este módulo NUNCA debe instalarse en una base de datos
de producción.** Está pensado para instalarse en una base separada
(ej. `odoo19_demo`), nunca en la base real de la empresa. Ver
`README.md` para el porqué de esa separación.

Reproducible por semilla (`DEMO_SEED`), con tres modos (SMALL,
STANDARD, STRESS) y un mecanismo explícito `ALLOW_REAL_DIAN = False`
que impide por diseño que un documento DEMO se envíe a la DIAN real.
""",
    'author': 'ERP Colombia',
    'license': 'LGPL-3',
    'depends': [
        'erp_colombia_core',
        'erp_colombia_terceros',
        'erp_colombia_empresa',
        'erp_colombia_contabilidad',
        'sale_management',
        'purchase',
        'stock',
        'account',
        'l10n_co',
        'l10n_co_electronic_invoice_self',
    ],
    'external_dependencies': {
        'python': ['faker'],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/demo_batch_views.xml',
        'wizard/demo_cleanup_wizard_views.xml',
        'views/demo_menu_views.xml',
    ],
    'installable': True,
}
