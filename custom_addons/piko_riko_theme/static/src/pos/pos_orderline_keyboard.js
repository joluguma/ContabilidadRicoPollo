import { patch } from "@web/core/utils/patch";
import { useExternalListener } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

// Fase 23: navegar el tique (las líneas ya agregadas a la venta) con
// las flechas — complementa la Fase 22, que hace lo mismo pero para la
// lista de RESULTADOS DE BÚSQUEDA. Los dos casos no se pisan: este solo
// actúa cuando el buscador está vacío (si hay una búsqueda activa, es
// la Fase 22 la que responde a las flechas).
//
// Seleccionar una línea con las flechas hace exactamente lo mismo que
// hacer clic en ella (this.pos.selectOrderLine) — no se duplica
// lógica de selección.
patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        useExternalListener(window, "keydown", this.onOrderlineKeydown.bind(this), {
            capture: true,
        });
    },

    // Mismo orden que OrderDisplay.comboSortedLines (addons/point_of_sale/
    // .../order_display.js) — se repite acá porque ese getter vive en otro
    // componente, pero tiene que ser EXACTAMENTE el mismo orden que lo que
    // se ve en pantalla para que la flecha mueva la selección a la línea
    // correcta.
    get piko_orderedLines() {
        const order = this.pos.getOrder();
        if (!order) {
            return [];
        }
        return order.lines.reduce((acc, line) => {
            if (line.combo_line_ids?.length > 0) {
                acc.push(line, ...line.combo_line_ids);
            } else if (!line.combo_parent_id) {
                acc.push(line);
            }
            return acc;
        }, []);
    },

    onOrderlineKeydown(ev) {
        if (this.pos.searchProductWord.trim()) {
            return; // buscador activo: eso lo maneja la Fase 22
        }
        if (!["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"].includes(ev.key)) {
            return;
        }
        const lines = this.piko_orderedLines;
        if (!lines.length) {
            return;
        }
        const order = this.pos.getOrder();
        const current = order.getSelectedOrderline();
        const currentIndex = current ? lines.findIndex((l) => l.uuid === current.uuid) : -1;

        let nextIndex;
        if (["ArrowDown", "ArrowRight"].includes(ev.key)) {
            nextIndex = currentIndex === -1 ? 0 : Math.min(currentIndex + 1, lines.length - 1);
        } else {
            nextIndex = Math.max(currentIndex - 1, 0);
        }

        ev.preventDefault();
        this.numberBuffer.reset(); // mismo comportamiento que clickLine() al cambiar de línea
        this.pos.selectOrderLine(order, lines[nextIndex]);
    },
});
