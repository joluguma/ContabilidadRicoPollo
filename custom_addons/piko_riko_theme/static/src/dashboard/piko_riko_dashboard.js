import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";
import { session } from "@web/session";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const PERIODS = [
    { key: "today", label: "Hoy" },
    { key: "week", label: "Semana" },
    { key: "month", label: "Mes" },
    { key: "year", label: "Año" },
];

const QUICK_ACTIONS = [
    { key: "factura", label: "Nueva factura", icon: "fa-file-text-o",
      xmlid: "account.action_move_out_invoice_type", ctx: { default_move_type: "out_invoice" } },
    { key: "venta", label: "Nueva venta", icon: "fa-shopping-cart",
      xmlid: "sale.action_quotations", ctx: {} },
    { key: "cliente", label: "Nuevo cliente", icon: "fa-user-plus",
      xmlid: "contacts.action_contacts", ctx: {} },
    { key: "compra", label: "Nueva compra", icon: "fa-truck",
      xmlid: "purchase.purchase_rfq", ctx: {} },
    { key: "producto", label: "Nuevo producto", icon: "fa-cube",
      xmlid: "product.product_template_action", ctx: {} },
];

class PikoRikoDashboard extends Component {
    static template = "piko_riko_theme.Dashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.periods = PERIODS;
        this.quickActions = QUICK_ACTIONS;
        this.state = useState({ data: null, loading: true, period: "month" });
        onWillStart(() => this.loadData());
    }

    async loadData() {
        this.state.loading = true;
        this.state.data = await this.orm.call(
            "piko.riko.dashboard", "get_dashboard_data", [this.state.period]);
        this.state.loading = false;
    }

    setPeriod(key) {
        if (this.state.period === key) return;
        this.state.period = key;
        this.loadData();
    }

    // --- Encabezado ---
    get greeting() {
        const h = new Date().getHours();
        const saludo = h < 12 ? "Buenos días" : h < 19 ? "Buenas tardes" : "Buenas noches";
        const nombre = (user.name || "").split(" ")[0];
        return `${saludo}, ${nombre}`;
    }

    get companyName() {
        return session.user_companies?.allowed_companies?.[session.user_companies.current_company]?.name
            || "GRUPO RICO POLLO SAS";
    }

    get periodLabel() {
        const map = { today: "hoy", week: "esta semana", month: "este mes", year: "este año" };
        return map[this.state.period] || "";
    }

    // --- Formato ---
    money(v) {
        const s = this.state.data?.kpis?.moneda || "$";
        return `${s} ${Math.round(v || 0).toLocaleString("es-CO")}`;
    }
    num(v) {
        return Math.round(v || 0).toLocaleString("es-CO");
    }
    relTime(iso) {
        if (!iso) return "";
        const d = new Date(iso.replace(" ", "T") + "Z");
        const diff = (Date.now() - d.getTime()) / 1000;
        if (diff < 60) return "hace instantes";
        if (diff < 3600) return `hace ${Math.floor(diff / 60)} min`;
        if (diff < 86400) return `hace ${Math.floor(diff / 3600)} h`;
        if (diff < 604800) return `hace ${Math.floor(diff / 86400)} d`;
        return d.toLocaleDateString("es-CO");
    }

    // --- Tarjetas KPI ---
    get cards() {
        const k = this.state.data?.kpis || {};
        return [
            { key: "ventas", icon: "fa-line-chart", label: `Ventas (${this.periodLabel})`,
              value: this.money(k.ventas), variation: k.ventas_var },
            { key: "compras", icon: "fa-truck", label: `Compras (${this.periodLabel})`,
              value: this.money(k.compras), variation: k.compras_var },
            { key: "utilidad", icon: "fa-balance-scale", label: `Utilidad (${this.periodLabel})`,
              value: this.money(k.utilidad),
              tone: (k.utilidad || 0) >= 0 ? "positive" : "negative" },
            { key: "valor_inventario", icon: "fa-cubes", label: "Valor de inventario",
              value: this.money(k.valor_inventario) },
            { key: "cxc", icon: "fa-arrow-down", label: "Cuentas por cobrar",
              value: this.money(k.cuentas_por_cobrar),
              sub: `${this.num(k.facturas_pendientes)} pendientes` },
            { key: "cxp", icon: "fa-arrow-up", label: "Cuentas por pagar",
              value: this.money(k.cuentas_por_pagar) },
            { key: "pedidos", icon: "fa-clock-o", label: "Pedidos por facturar",
              value: this.num(k.pedidos_pendientes) },
            { key: "stock_bajo", icon: "fa-exclamation-triangle", label: "Productos con stock bajo",
              value: this.num(k.stock_bajo),
              tone: (k.stock_bajo || 0) > 0 ? "warning" : "positive" },
        ];
    }

    // --- Acciones rápidas ---
    async quickAction(qa) {
        await this.action.doAction(qa.xmlid, {
            additionalContext: qa.ctx,
            viewType: "form",
        });
    }

    // --- Alertas ---
    openAlert(key) {
        const today = new Date().toISOString().slice(0, 10);
        const acts = {
            stock_bajo: {
                type: "ir.actions.act_window",
                name: "Productos con stock bajo",
                res_model: "product.template",
                domain: [["is_storable", "=", true]],
                context: { search_default_below_min_stock: 1 },
                views: [[false, "list"], [false, "form"]],
            },
            facturas_pendientes: {
                type: "ir.actions.act_window",
                name: "Facturas por cobrar",
                res_model: "account.move",
                domain: [
                    ["move_type", "=", "out_invoice"], ["state", "=", "posted"],
                    ["payment_state", "in", ["not_paid", "partial"]],
                ],
                views: [[false, "list"], [false, "form"]],
            },
            cartera_vencida: {
                type: "ir.actions.act_window",
                name: "Cartera vencida",
                res_model: "account.move",
                domain: [
                    ["move_type", "=", "out_invoice"], ["state", "=", "posted"],
                    ["payment_state", "in", ["not_paid", "partial"]],
                    ["invoice_date_due", "<", today],
                ],
                views: [[false, "list"], [false, "form"]],
            },
        };
        if (acts[key]) this.action.doAction(acts[key]);
    }
}

registry.category("actions").add("piko_riko_dashboard", PikoRikoDashboard);

export default PikoRikoDashboard;
