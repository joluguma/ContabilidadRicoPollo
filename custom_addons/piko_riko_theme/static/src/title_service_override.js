import { registry } from "@web/core/registry";

// Reemplaza el servicio nativo de título de pestaña del navegador: la
// única diferencia con el original es el texto de respaldo cuando no
// hay ninguna sección activa ("Piko Riko" en vez de "Odoo").
const pikoRikoTitleService = {
    start() {
        const titleCounters = {};
        const titleParts = {};

        function setCounters(counters) {
            for (const key in counters) {
                const val = counters[key];
                if (!val) {
                    delete titleCounters[key];
                } else {
                    titleCounters[key] = val;
                }
            }
            updateTitle();
        }

        function setParts(parts) {
            for (const key in parts) {
                const val = parts[key];
                if (!val) {
                    delete titleParts[key];
                } else {
                    titleParts[key] = val;
                }
            }
            updateTitle();
        }

        function updateTitle() {
            const counter = Object.values(titleCounters).reduce((acc, count) => acc + count, 0);
            const name = Object.values(titleParts).join(" - ") || "Piko Riko";
            document.title = counter ? `(${counter}) ${name}` : name;
        }

        return {
            get current() {
                return document.title;
            },
            getParts: () => Object.assign({}, titleParts),
            setCounters,
            setParts,
        };
    },
};

registry.category("services").add("title", pikoRikoTitleService, { force: true });
