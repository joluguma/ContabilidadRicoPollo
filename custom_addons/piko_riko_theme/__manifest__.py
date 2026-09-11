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

Fase 8:
  * Logo oficial de GRUPO RICO POLLO S.A.S. (static/src/img/logo.png)
    cargado en la ficha de la compañía (res.company.logo) — se propaga
    a la página de login y a todos los PDF (facturas, órdenes, tirilla,
    cotizaciones). Favicon (símbolo del logo) vía
    views/favicon_templates.xml. El título del documento HTML deja de
    decir "Odoo".
  * Rediseño de la página de inicio de sesión: tarjeta blanca centrada
    con sombra suave, logo grande, campos y botón con la identidad de
    marca (rojo/amarillo), franja de acento arriba, modo oscuro y
    responsive. Cambios de plantilla mínimos; el diseño vive en
    static/src/scss/piko_riko_login.scss y aplica solo a las pantallas
    de autenticación.

Fase 9:
  * Pantalla de acceso rediseñada a dos paneles: izquierda identidad
    corporativa (tratamiento gráfico de marca con la geometría del
    logo, titular "Más que productos, soluciones", 4 beneficios),
    derecha acceso con correo + contraseña, 3 indicadores de confianza
    y pie legal. Responsive (tablet apila, móvil elimina el panel de
    marca), modo oscuro. Se quita el selector de usuarios de Odoo: el
    login siempre pide correo + contraseña.
  * Se eliminan las cuentas de PRUEBA que se usaron para testear los
    perfiles (scripts/borrar_usuarios_prueba.py).

Fase 10:
  * El color de ACCIÓN del sistema pasa de amarillo a rojo corporativo
    para combinar con la pantalla de acceso (botones, pestañas activas,
    foco, enlaces). El amarillo se conserva como acento: la línea
    inferior del navbar es un degradado rojo→amarillo, el mismo detalle
    que la franja de la pantalla de acceso. Fondo general a blanco
    cálido (#FCFBFA), igual que el login.
  * Dashboard convertido en centro de operaciones: saludo por hora del
    día, filtro de período (Hoy/Semana/Mes/Año) que recalcula los KPIs,
    fila de acciones rápidas (nueva factura/venta/cliente/compra/
    producto), panel "Requiere atención" (stock bajo, facturas por
    cobrar, cartera vencida — cada una abre la lista filtrada) y
    "Actividad reciente" (últimos documentos con usuario y hora). Todo
    con datos reales; no toca ningún módulo funcional ni la navegación.

Fase 11:
  * Punto de Venta: el modo sin conexión YA es nativo de Odoo (guarda
    los pedidos en el equipo y sincroniza solo al volver la señal) —
    no se programó nada nuevo, solo se hizo más claro el aviso que ya
    existía en la barra del POS (antes solo un ícono, ahora dice
    "Sin conexión" en texto).
  * Franja fija de módulos: segunda fila debajo de la barra superior,
    siempre visible, con todos los módulos instalados (antes había que
    abrir el menú de apps para verlos). Reusa los mismos datos/acciones
    del menú de apps nativo, no duplica lógica.
  * Dashboard: se agrega un gráfico "Ventas vs. compras (últimos 6
    meses)" y una lista "Más vendidos (30 días)" — datos reales,
    usando Chart.js (ya incluido en Odoo, no se agregó ninguna
    librería nueva).

Fase 12:
  * El menú de módulos pasa de franja horizontal (Fase 11) a menú
    vertical, de arriba a abajo, a pedido explícito del cliente —
    reemplaza la franja, no coexisten. Cada módulo lleva un ícono en
    un chip de color (paleta fija rotativa, "íconos llamativos").
    Colapsable a solo íconos, con la preferencia guardada en el
    navegador de cada usuario.

Fase 13:
  * Íconos del menú vertical: se reemplazan los chips genéricos por
    emoji reales, uno por módulo, elegidos junto con el cliente
    (Inicio, Contactos, Ventas, Compras, Inventario, Facturación,
    Punto de Venta, Empleados, Configuración). Se ocultan del menú (sin
    desinstalar, reversible) los módulos "ERP Colombia" y "Tableros"
    (spreadsheet_dashboard) a pedido del cliente — el módulo propio
    "Dashboard" (nuestro centro de operaciones) se mantiene.

Fase 14:
  * Tirilla de venta rediseñada: mayor jerarquía visual del TOTAL (caja
    con doble línea, tipografía grande), tipo y número de documento del
    cliente mostrados con los campos reales de Odoo (identificación
    colombiana ya nativa, no se inventó ningún campo), detalle de pago
    con el desglose REAL por medio de pago (efectivo/tarjeta/etc.)
    cuando la factura viene de una venta de Punto de Venta, y bloque de
    observaciones si la factura tiene notas. Se agrega la opción
    "Tirilla 58mm" junto a la de 80mm ya existente (menú Imprimir de la
    factura), reutilizando el mismo diseño con tipografía y anchos
    ajustados.
  * Se agrega un QR de referencia del cliente (con su NOMBRE, nunca su
    cédula/NIT) a modo de maqueta visual, a pedido explícito del
    cliente para ver cómo se ve en la tirilla — pendiente de definir
    con el cliente su uso definitivo.
  * Se evalúo y se descartó deliberadamente agregar resolución DIAN,
    CUFE y QR fiscal simulados/inventados: el sistema todavía no tiene
    habilitación real ante la DIAN, y mostrar esos datos falsos
    convertiría la tirilla en un documento que aparenta ser una factura
    electrónica válida sin serlo (riesgo de falsedad documental/
    tributaria) — se mantiene "FACTURA DE VENTA", tal como se decidió
    en la Fase 2.5.

Fase 15:
  * Se oculta el aviso "Esta es una vista previa del portal de clientes"
    que aparece al navegar el portal como usuario interno (vendedor/
    administrador) — un cliente real nunca lo ve (es exclusivo de la
    vista de vendedores), pero llevaba a una pantalla del backend que
    no hacía falta al solo revisar el pedido/factura del cliente.

Fase 16:
  * Impresión directa de la tirilla: al elegir "Imprimir → Factura -
    Tirilla 80mm/58mm" ya no se descarga el PDF a la carpeta de
    Descargas — se abre una pestaña con el diseño ya listo y el
    navegador muestra de una vez el diálogo de imprimir (el usuario
    solo confirma "Imprimir" una vez). Las opciones para descargar/
    enviar el PDF normal se mantienen intactas para cuando sí haga
    falta guardarlo o adjuntarlo a un correo.
  * Se oculta el botón de grilla (⊞) arriba a la izquierda: abría el
    mismo listado de apps que ya está siempre visible en el menú
    vertical — quedaba redundante. Sigue disponible en pantallas
    pequeñas, donde el menú vertical no se muestra.
  * Íconos en el menú horizontal de cada app (Clientes, Proveedores,
    Reportes, Configuración, etc.), igual que se hizo con el menú
    vertical — un solo mapa por palabra clave que aplica en todas las
    apps sin mantener una lista distinta por cada una.

Fase 17:
  * El botón "Imprimir" de la factura (el de arriba, no el menú
    "Imprimir → ...") ahora abre de una vez la tirilla con impresión
    directa — antes abría la factura A4 estándar en inglés, sin QR,
    porque ese botón usa un mecanismo distinto al menú de reportes
    (no tenía nada que ver con la Fase 16). El botón "Enviar" (correo)
    NO cambia: sigue adjuntando la factura A4 estándar, más adecuada
    para un correo que la tirilla angosta.
  * Logo de la compañía junto al nombre, arriba a la derecha (donde ya
    se mostraba el nombre de la compañía) — antes solo aparecía en el
    login y en los PDF.

Fase 18:
  * Logo de la compañía en la pantalla del Punto de Venta (arriba,
    centrado, cuando no hay una orden activa — así lo muestra el
    propio POS de Odoo). No es código nuevo: POS ya traía el mecanismo,
    solo mostraba el logo de Odoo por defecto porque nadie lo había
    apuntado al logo real.
  * Se corrigió que la caja no mostraba NINGÚN producto: ninguno de
    los productos tenía marcada la casilla "Disponible en PdV" (dato,
    no código — se corrigió directamente en la base de datos para
    todos los productos vendibles).

Pendiente para fases siguientes (ver ARCHITECTURE.md):
  * Vistas de inventario/productos con badges de stock.
  * Vista kanban de cotizaciones con badges de estado.
  * Ajustes responsive/móvil adicionales.
""",
    'author': 'Piko Riko',
    'license': 'LGPL-3',
    'depends': ['web', 'sale', 'purchase', 'account', 'stock', 'mail', 'point_of_sale'],
    'data': [
        'views/dashboard_menu.xml',
        'views/login_templates.xml',
        'views/favicon_templates.xml',
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
            'piko_riko_theme/static/src/nav/piko_riko_sidebar.js',
            'piko_riko_theme/static/src/nav/piko_riko_sidebar.xml',
            'piko_riko_theme/static/src/nav/piko_riko_sidebar.scss',
            'piko_riko_theme/static/src/nav/piko_riko_submenu_icons.js',
            'piko_riko_theme/static/src/nav/piko_riko_submenu_icons.xml',
            'piko_riko_theme/static/src/nav/piko_riko_submenu_icons.scss',
            'piko_riko_theme/static/src/nav/piko_riko_topbar_logo.xml',
            'piko_riko_theme/static/src/nav/piko_riko_topbar_logo.scss',
            'piko_riko_theme/static/src/reports/tirilla_direct_print.js',
        ],
        'web.report_assets_common': [
            'piko_riko_theme/static/src/scss/piko_riko_report_fix.scss',
        ],
        'web.assets_frontend': [
            'piko_riko_theme/static/src/scss/piko_riko_login.scss',
            'piko_riko_theme/static/src/scss/piko_riko_portal.scss',
        ],
        'point_of_sale.assets_prod': [
            'piko_riko_theme/static/src/pos/pos_offline_notice.xml',
            'piko_riko_theme/static/src/pos/pos_branding.scss',
        ],
    },
    'installable': True,
    'application': True,
}
