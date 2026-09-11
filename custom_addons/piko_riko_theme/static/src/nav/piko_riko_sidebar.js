import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";
import { useState } from "@odoo/owl";

// Fase 12: menú vertical de módulos.
// Fase 13: íconos pedidos explícitamente por el cliente (emoji reales,
// no íconos de librería — así de "llamativos" como se pidió) y dos
// módulos ocultos por ahora a pedido del cliente.
const PIKO_APP_ICONS = {
    "piko_riko_theme.menu_piko_riko_dashboard_root": "🏠", // Inicio
    "contacts.menu_contacts": "👥", // Comercial / contactos
    "sale.sale_menu_root": "📈", // Ventas (no se dio ícono explícito, se eligió uno afín)
    "purchase.menu_purchase_root": "🛒", // Compras
    "stock.menu_stock_root": "📦", // Inventario
    "account.menu_finance": "💰", // Finanzas / Facturación
    "point_of_sale.menu_point_root": "🧾", // Punto de venta
    "hr.menu_hr_root": "👨‍💼", // Empleados
    "base.menu_administration": "⚙️", // Configuración
};
const PIKO_DEFAULT_ICON = "🔹";

// Ocultos por ahora, a pedido explícito del cliente (no se desinstala
// nada, solo se quitan del menú — reversible).
const PIKO_HIDDEN_APP_XMLIDS = new Set([
    "erp_colombia_core.menu_erp_colombia_root", // "ERP Colombia"
    "spreadsheet_dashboard.spreadsheet_dashboard_menu_root", // "Tableros"/"Dashboards"
]);

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
        // El área de contenido (.o_action_manager) vive fuera de este
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

    pikoVisibleApps() {
        return this.menuService.getApps().filter((app) => !PIKO_HIDDEN_APP_XMLIDS.has(app.xmlid));
    },

    pikoAppIcon(app) {
        return PIKO_APP_ICONS[app.xmlid] || PIKO_DEFAULT_ICON;
    },
});
