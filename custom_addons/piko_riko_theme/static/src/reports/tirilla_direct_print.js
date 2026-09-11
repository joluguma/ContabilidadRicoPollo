import { registry } from "@web/core/registry";

/* Fase 16: impresión directa de la tirilla.
 *
 * Por defecto, Odoo SIEMPRE descarga los reportes PDF (ver
 * addons/web/static/src/webclient/actions/reports/utils.js:downloadReport) —
 * no es una configuración del navegador, es el comportamiento estándar del
 * cliente web. Eso obligaba a: descargar el PDF → ir a Descargas → abrirlo →
 * recién ahí imprimir.
 *
 * Este handler se registra en el punto de extensión oficial
 * "ir.actions.report handlers" (ver action_service.js) e intercepta
 * SOLO nuestras dos acciones de tirilla: en vez de descargar el PDF, abre
 * en una pestaña nueva una versión HTML mínima que dispara el diálogo de
 * impresión del navegador apenas carga (ver
 * report_invoice_receipt_print[_58] en receipt_invoice_report.xml). El
 * usuario solo confirma "Imprimir" una vez, sin tener que buscar el
 * archivo descargado.
 *
 * Esto NO es impresión 100% silenciosa (ningún sitio web puede saltarse el
 * diálogo nativo del navegador sin un permiso especial del sistema) — para
 * eso se necesitaría configurar el Chrome de la caja registradora en modo
 * kiosco de impresión (--kiosk-printing), que es una configuración del
 * equipo, no algo que el sistema pueda forzar por sí solo.
 */
const DIRECT_PRINT_TEMPLATES = {
    "piko_riko_theme.report_invoice_receipt": "piko_riko_theme.report_invoice_receipt_print",
    "piko_riko_theme.report_invoice_receipt_58": "piko_riko_theme.report_invoice_receipt_print_58",
};

registry.category("ir.actions.report handlers").add("piko_riko_tirilla_direct_print", async (action) => {
    const printTemplate = DIRECT_PRINT_TEMPLATES[action.report_name];
    if (!printTemplate) {
        return false; // no es una de nuestras tirillas: seguir con el flujo normal de Odoo
    }
    const activeIds = (action.context && action.context.active_ids) || [];
    if (!activeIds.length) {
        return false;
    }
    window.open(`/report/html/${encodeURIComponent(printTemplate)}/${activeIds.join(",")}`, "_blank");
    return true; // manejado: no descargar el PDF
});
