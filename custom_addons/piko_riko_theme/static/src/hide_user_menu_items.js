/** @odoo-module **/
import { registry } from "@web/core/registry";

// Se quitan del menú de usuario (arriba a la derecha) los accesos que
// no aplican a un negocio con self-hosting propio: "Instalar
// aplicación" (PWA), "Mi cuenta de Odoo.com" (cuenta en odoo.com, no
// existe para este servidor) y "Mis preferencias" (idioma/foto, poco
// usado, genera confusión). Reversible: solo se remueven del registro,
// no se borra funcionalidad real.
const userMenuItems = registry.category("user_menuitems");
for (const key of ["preferences", "odoo_account", "install_pwa"]) {
    if (userMenuItems.contains(key)) {
        userMenuItems.remove(key);
    }
}
