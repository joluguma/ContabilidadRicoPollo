/** @odoo-module **/
import { registry } from "@web/core/registry";

// Se quita el ícono de chat (mensajería interna) y el de actividades
// pendientes de la barra superior — el negocio no usa mensajería
// interna todavía (ver Fase 3.1: Discuss ya está oculto como app) y
// las notificaciones de actividades no aportan valor por ahora. Es
// reversible: solo se remueven del registro de íconos, no se
// desinstala ni se rompe el módulo mail (el chatter de documentos
// sigue funcionando igual).
const systray = registry.category("systray");
if (systray.contains("mail.messaging_menu")) {
    systray.remove("mail.messaging_menu");
}
if (systray.contains("mail.activity_menu")) {
    systray.remove("mail.activity_menu");
}
