import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";

// Fase 16: íconos para el menú horizontal de cada app (Clientes,
// Proveedores, Reportes, Configuración, etc. — el que aparece debajo de la
// barra superior), pedido explícito del cliente para que se vea igual de
// "llamativo" que el menú vertical de apps. Es un mapa por PALABRA CLAVE
// (no por app): las mismas palabras ("Reportes", "Configuración", etc.) se
// repiten en casi todas las apps, así que un solo mapa cubre Ventas,
// Compras, Inventario, Facturación, POS, Empleados, etc. sin tener que
// mantener una lista distinta por app.
const PIKO_SECTION_ICON_KEYWORDS = [
    // Comercial / contactos
    [["cliente"], "fa-users"],
    [["proveedor"], "fa-truck"],
    [["contacto"], "fa-address-book"],

    // Ventas
    [["cotizacion", "presupuesto"], "fa-file-text-o"],
    [["pedido", "orden de venta"], "fa-shopping-cart"],
    [["venta"], "fa-line-chart"],

    // Compras
    [["compra", "solicitud de compra"], "fa-shopping-basket"],

    // Facturación / contabilidad
    [["factura"], "fa-file-text-o"],
    [["pago"], "fa-money"],
    [["asiento", "diario"], "fa-book"],
    [["impuesto"], "fa-percent"],
    [["banco", "efectivo"], "fa-university"],
    [["conciliacion"], "fa-check-square-o"],
    [["cliente a cobrar", "cartera"], "fa-arrow-down"],

    // Inventario
    [["producto"], "fa-cube"],
    [["recepcion"], "fa-truck"],
    [["entrega"], "fa-truck"],
    [["traslado"], "fa-exchange"],
    [["ajuste de inventario", "conteo"], "fa-balance-scale"],
    [["categoria"], "fa-folder-o"],
    [["bodega", "almacen"], "fa-building-o"],

    // Punto de venta
    [["sesion"], "fa-desktop"],
    [["orden"], "fa-shopping-cart"],

    // Empleados / RRHH
    [["empleado"], "fa-user"],
    [["contrato"], "fa-file-text"],
    [["nomina"], "fa-money"],
    [["vacacion", "ausencia"], "fa-calendar"],
    [["reclutamiento", "postulante"], "fa-search"],
    [["evaluacion"], "fa-star-o"],

    // Comunes a casi todas las apps
    [["reporte", "informe", "analisis"], "fa-bar-chart"],
    [["configuracion", "ajuste"], "fa-cog"],
    [["usuario"], "fa-user-circle-o"],
    [["tablero", "panel"], "fa-th-large"],
];

function pikoNormalize(text) {
    return (text || "")
        .toLowerCase()
        .normalize("NFD")
        .replace(/[̀-ͯ]/g, ""); // quita tildes (marcas diacríticas combinantes)
}

patch(NavBar.prototype, {
    pikoSectionIcon(section) {
        const name = pikoNormalize(section.name);
        for (const [keywords, icon] of PIKO_SECTION_ICON_KEYWORDS) {
            if (keywords.some((kw) => name.includes(kw))) {
                return icon;
            }
        }
        return "fa-circle-o"; // sin match conocido: ícono genérico discreto, no se deja vacío
    },
});
