# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
{
    'name': 'Piko Riko - Tema Visual',
    'version': '19.0.1.0.0',
    'category': 'Themes',
    'summary': 'Identidad visual de Piko Riko para el ERP (colores, botones, login)',
    'description': """
Piko Riko - Tema Visual
=======================

Módulo de solo apariencia (no toca lógica de negocio ni datos). Aplica
la identidad de marca de Piko Riko sobre el backend estándar de Odoo:

Fase 1:
  * Paleta de marca (amarillo/rojo de Piko Riko) aplicada a botones,
    estados activos y elementos de foco, sin saturar la interfaz.
  * Botones con bordes redondeados y sombra sutil.
  * Logo de la compañía (res.company.logo) usado automáticamente en
    login, encabezado y reportes — es el mecanismo nativo de Odoo,
    solo hace falta cargar el archivo de imagen en la ficha de la
    compañía.

Fase 2:
  * Dashboard con KPIs (ventas del día/mes, compras, inventario
    disponible, productos con stock bajo, cartera por cobrar/pagar,
    utilidad aproximada, facturas y pedidos pendientes).

Fase 2.1 (este módulo, por ahora):
  * Corrección de un bug real de wkhtmltopdf (el motor que genera los
    PDF) que dejaba invisible el contenido de columnas en cotizaciones,
    facturas y demás reportes — se veía bien en el navegador pero no
    en el PDF descargado/enviado.

Fase 2.2:
  * Marca propia: se reemplaza "Odoo" por "Piko Riko" en el pie del
    login y en el título de la pestaña del navegador.

Fase 2.3:
  * Impresión de facturas en tirilla térmica de 80mm, como opción
    adicional junto al PDF normal (menú Imprimir de la factura).

Fase 3 (probada en demo, DESCARTADA a pedido del cliente):
  * Se construyó una barra lateral de navegación colapsable como
    reemplazo de la barra horizontal nativa de Odoo. El cliente revisó
    el resultado y decidió no adoptarla — se mantiene la navegación
    estándar de Odoo. Código removido de este módulo; si se retoma más
    adelante, ver el historial de este archivo.

Pendiente para fases siguientes (ver ARCHITECTURE.md):
  * Vistas de inventario/productos con badges de stock.
  * Vista kanban de cotizaciones con badges de estado.
  * Ajustes responsive/móvil adicionales.
""",
    'author': 'Piko Riko',
    'license': 'LGPL-3',
    'depends': ['web', 'sale', 'purchase', 'account', 'stock'],
    'data': [
        'views/dashboard_menu.xml',
        'views/login_templates.xml',
        'data/paperformat_receipt.xml',
        'report/receipt_invoice_report.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'piko_riko_theme/static/src/scss/piko_riko_variables.scss'),
        ],
        'web.assets_backend': [
            'piko_riko_theme/static/src/scss/piko_riko_backend.scss',
            'piko_riko_theme/static/src/title_service_override.js',
            'piko_riko_theme/static/src/dashboard/piko_riko_dashboard.js',
            'piko_riko_theme/static/src/dashboard/piko_riko_dashboard.xml',
            'piko_riko_theme/static/src/dashboard/piko_riko_dashboard.scss',
        ],
        'web.report_assets_common': [
            'piko_riko_theme/static/src/scss/piko_riko_report_fix.scss',
        ],
    },
    'installable': True,
    'application': True,
}
