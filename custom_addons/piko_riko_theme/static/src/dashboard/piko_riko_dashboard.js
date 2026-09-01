import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

class PikoRikoDashboard extends Component {
    static template = "piko_riko_theme.Dashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ kpis: null, loading: true });
        onWillStart(() => this.loadKpis());
    }

    async loadKpis() {
        this.state.loading = true;
        this.state.kpis = await this.orm.call("piko.riko.dashboard", "get_kpis", []);
        this.state.loading = false;
    }

    formatMoney(value) {
        const symbol = this.state.kpis?.moneda_simbolo || "$";
        const rounded = Math.round(value || 0);
        return `${symbol} ${rounded.toLocaleString("es-CO")}`;
    }

    formatNumber(value) {
        return Math.round(value || 0).toLocaleString("es-CO");
    }

    get cards() {
        const k = this.state.kpis || {};
        return [
            {
                key: "ventas_dia",
                icon: "fa-shopping-cart",
                label: "Ventas del día",
                value: this.formatMoney(k.ventas_dia),
            },
            {
                key: "ventas_mes",
                icon: "fa-line-chart",
                label: "Ventas del mes",
                value: this.formatMoney(k.ventas_mes),
                variation: k.ventas_mes_variacion_pct,
            },
            {
                key: "compras_mes",
                icon: "fa-truck",
                label: "Compras del mes",
                value: this.formatMoney(k.compras_mes),
            },
            {
                key: "utilidad_mes",
                icon: "fa-percent",
                label: "Utilidad del mes",
                value: this.formatMoney(k.utilidad_mes),
                tone: (k.utilidad_mes || 0) >= 0 ? "positive" : "negative",
            },
            {
                key: "inventario_disponible",
                icon: "fa-cubes",
                label: "Inventario disponible",
                value: this.formatNumber(k.inventario_disponible),
                suffix: "unidades",
            },
            {
                key: "valor_inventario",
                icon: "fa-money",
                label: "Valor de inventario",
                value: this.formatMoney(k.valor_inventario),
            },
            {
                key: "stock_bajo",
                icon: "fa-exclamation-triangle",
                label: "Productos con stock bajo",
                value: this.formatNumber(k.stock_bajo),
                tone: (k.stock_bajo || 0) > 0 ? "warning" : "positive",
            },
            {
                key: "cuentas_por_cobrar",
                icon: "fa-arrow-down",
                label: "Cuentas por cobrar",
                value: this.formatMoney(k.cuentas_por_cobrar),
            },
            {
                key: "cuentas_por_pagar",
                icon: "fa-arrow-up",
                label: "Cuentas por pagar",
                value: this.formatMoney(k.cuentas_por_pagar),
            },
            {
                key: "facturas_pendientes",
                icon: "fa-file-text-o",
                label: "Facturas pendientes",
                value: this.formatNumber(k.facturas_pendientes),
            },
            {
                key: "pedidos_pendientes",
                icon: "fa-clock-o",
                label: "Pedidos pendientes",
                value: this.formatNumber(k.pedidos_pendientes),
            },
        ];
    }
}

registry.category("actions").add("piko_riko_dashboard", PikoRikoDashboard);

export default PikoRikoDashboard;
