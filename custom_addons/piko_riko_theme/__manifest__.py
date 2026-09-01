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

Fase 2.4:
  * Reintento automático (hasta 3 veces) cuando wkhtmltopdf falla con
    el código -11 (segfault intermitente por correr traducido con
    Rosetta 2 en Apple Silicon, sin build nativo disponible) — el
    usuario ya no tiene que darle "Imprimir" de nuevo a mano.

Fase 3 (probada en demo, DESCARTADA a pedido del cliente):
  * Se construyó una barra lateral de navegación colapsable como
    reemplazo de la barra horizontal nativa de Odoo. El cliente revisó
    el resultado y decidió no adoptarla — se mantiene la navegación
    estándar de Odoo. Código removido de este módulo; si se retoma más
    adelante, ver el historial de este archivo.

Fase 3.1:
  * Se oculta la app "Discuss" (Conversaciones) del selector de apps y
    del menú superior — no se usará por ahora. La mensajería interna,
    el chatter y las notificaciones NO se desactivan (siguen
    funcionando igual); solo desaparece como app independiente. Es
    reversible.

Fase 2.5:
  * La tirilla de 80mm se rediseñó para parecerse a los comprobantes
    de venta que el negocio ya conoce (encabezado con datos de la
    empresa, datos del cliente, tabla de artículos con precio
    unitario/cantidad/valor, estado de pago). Dice deliberadamente
    "Factura de Venta" (sin "Electrónica") y NO incluye CUFE ni código
    QR: esos solo los puede emitir un sistema con habilitación real
    ante la DIAN (certificado digital) — trámite pendiente, no algo
    que se pueda simular sin hacerlo pasar por algo que no es.

Fase 4 (este módulo, por ahora):
  * Colores semánticos de estado contable: se afinan $success/$warning
    (verde=pagado/conciliado, naranja=pendiente — deliberadamente
    distinto del amarillo de marca para no confundirlos) sobre el
    mecanismo NATIVO de badges de Odoo (widget="badge"
    decoration-success/warning/info), así que aplica automáticamente en
    toda la app (facturas, pagos, asientos) sin vistas nuevas.
  * Tipografía tabular en columnas numéricas de las listas (plan de
    cuentas, facturas, etc.) — usa la clase nativa "o_list_number" que
    Odoo ya pone en toda columna de cifras.
  * Modo oscuro (primera versión): sigue la preferencia del sistema
    operativo/navegador automáticamente, sin botón. Cobertura: fondo
    general, tarjetas de vista, tablas, inputs. Vistas muy específicas
    podrían necesitar ajustes puntuales más adelante.

Fase 5:
  * Se quita el ícono de chat interno y el de actividades pendientes
    de la barra superior (no se usan todavía) — reversible, no afecta
    el chatter de documentos ni el módulo mail.
  * Se oculta la pestaña "Apps" de Ajustes: instalar/actualizar
    módulos queda solo por línea de comandos (lo hace el
    desarrollador), no expuesto en la interfaz web a ningún usuario.
  * Todos los usuarios quedan en español (es_419) por defecto.

Fase 7:
  * Valor de inventario (cantidad x costo): columna nueva "Valor
    inventario" en la lista de Productos de Inventario (con total al
    pie de la lista) y tarjeta nueva en el dashboard con el total
    general. Es solo de consulta — no genera asientos contables
    automáticos (decisión explícita: la valoración de las categorías
    de producto sigue siendo periódica/manual). El número solo es
    correcto una vez se haga el conteo físico real y se cargue la
    cantidad de cada producto — mientras tanto refleja únicamente los
    pocos productos que ya tienen cantidad cargada.

Pendiente para fases siguientes (ver ARCHITECTURE.md):
  * Vistas de inventario/productos con badges de stock.
  * Vista kanban de cotizaciones con badges de estado.
  * Ajustes responsive/móvil adicionales.
""",
    'author': 'Piko Riko',
    'license': 'LGPL-3',
    'depends': ['web', 'sale', 'purchase', 'account', 'stock', 'mail'],
    'data': [
        'views/dashboard_menu.xml',
        'views/login_templates.xml',
        'data/paperformat_receipt.xml',
        'data/hide_discuss_menu.xml',
        'data/hide_apps_menu.xml',
        'views/product_inventory_value_view.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_picking_location_domain.xml',
        'report/receipt_invoice_report.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'piko_riko_theme/static/src/scss/piko_riko_variables.scss'),
        ],
        'web.assets_backend': [
            'piko_riko_theme/static/src/scss/piko_riko_backend.scss',
            'piko_riko_theme/static/src/scss/piko_riko_dark_mode.scss',
            'piko_riko_theme/static/src/title_service_override.js',
            'piko_riko_theme/static/src/hide_chat_systray.js',
            'piko_riko_theme/static/src/hide_user_menu_items.js',
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
