import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";
import { useState } from "@odoo/owl";

// Fase 12: se pasa de la franja horizontal de módulos (Fase 11) a un
// menú vertical, a pedido del cliente. Se extiende la clase NavBar
// (no se toca el archivo original) solo para agregar el estado
// "colapsado/expandido" del menú — el resto (lista de apps, ícono,
// navegación) reusa exactamente los mismos datos/métodos que ya usa
// el propio NavBar nativo (menuService, getMenuItemHref,
// onNavBarDropdownItemSelection), ver piko_riko_sidebar.xml.
patch(NavBar.prototype, {
    setup() {
        super.setup();
        let collapsed = false;
        try {
            collapsed = JSON.parse(localStorage.getItem("piko_sidebar_collapsed") || "false");
        } catch {
            collapsed = false;
        }
        this.pikoSidebarState = useState({ collapsed });
        // El área de contenido (.o_content) vive fuera de este
        // componente (es hermano, no hijo, del navbar) — se marca en
        // <body> para poder correrle el margen izquierdo por CSS
        // cuando el menú se colapsa/expande.
        document.body.classList.toggle("o_piko_sidebar_collapsed", collapsed);
    },

    togglePikoSidebar() {
        this.pikoSidebarState.collapsed = !this.pikoSidebarState.collapsed;
        document.body.classList.toggle("o_piko_sidebar_collapsed", this.pikoSidebarState.collapsed);
        try {
            localStorage.setItem("piko_sidebar_collapsed", JSON.stringify(this.pikoSidebarState.collapsed));
        } catch {
            // localStorage puede fallar (modo privado, etc.) — no es crítico, se pierde solo la preferencia.
        }
    },
});
