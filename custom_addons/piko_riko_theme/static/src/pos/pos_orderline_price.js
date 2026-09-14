import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/components/orderline/orderline";

// Fase 20: en el tique (carrito) del POS, Odoo por defecto solo muestra el
// precio unitario debajo del nombre cuando la cantidad es distinta de 1
// (si es 1, el total de la línea YA es el precio unitario, así que lo
// oculta por no ser redundante). A pedido del cliente se quiere ver
// SIEMPRE, explícito, junto con el código del producto — como en el
// mockup de referencia ("$17.800,00 | ACEITE01").
//
// No se toca ningún cálculo: se reutiliza el mismo precio ya resuelto
// por Odoo (line.currencyDisplayPriceUnit), que ya respeta listas de
// precios, descuentos y reglas de precio — solo cambia cuándo se
// muestra ese texto, no de dónde sale el número.
patch(Orderline.prototype, {
    get lineScreenValues() {
        const vals = super.lineScreenValues;
        if (!this.line.order_id || this.props.mode !== "display" || !vals.price) {
            return vals;
        }
        const priceUnit = `${this.line.currencyDisplayPriceUnit} / ${this.line.product_id?.uom_id?.name || ""}`;
        const sku = this.line.product_id?.default_code;
        vals.displayPriceUnit = sku ? `${priceUnit} | ${sku}` : priceUnit;
        return vals;
    },
});
