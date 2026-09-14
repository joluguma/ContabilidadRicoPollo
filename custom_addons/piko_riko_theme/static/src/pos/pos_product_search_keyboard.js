import { patch } from "@web/core/utils/patch";
import { useExternalListener } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

// Fase 22: cuando se está buscando un producto por teclado, permitir
// moverse por la lista de resultados con las flechas y agregar el
// resaltado con Enter — sin esto, había que soltar el teclado y hacer
// clic con el mouse para elegir cuál de los resultados es.
//
// Solo actúa mientras hay una palabra de búsqueda activa (el escenario
// exacto que se pidió: "cuando se esté buscando el producto"). Fuera de
// eso, las flechas se dejan tal cual (por ejemplo, para moverse dentro
// del texto que se está escribiendo).
patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.state.highlightedProductIndex = -1;
        this.state.highlightedSearchWord = "";
        useExternalListener(window, "keydown", this.onProductSearchKeydown.bind(this), {
            capture: true,
        });
    },

    get piko_searchResultsList() {
        return this.pos.productsToDisplay;
    },

    onProductSearchKeydown(ev) {
        const searchWord = this.pos.searchProductWord.trim();
        if (!searchWord) {
            return;
        }
        const list = this.piko_searchResultsList;

        // La lista cambió desde la última tecla (se escribió algo
        // nuevo en el buscador) — se reinicia el resaltado en vez de
        // dejarlo apuntando a un índice de la búsqueda anterior.
        if (this.state.highlightedSearchWord !== searchWord) {
            this.state.highlightedSearchWord = searchWord;
            this.state.highlightedProductIndex = -1;
        }

        if (["ArrowDown", "ArrowRight"].includes(ev.key)) {
            ev.preventDefault();
            if (!list.length) {
                return;
            }
            this.state.highlightedProductIndex = Math.min(
                this.state.highlightedProductIndex + 1,
                list.length - 1
            );
        } else if (["ArrowUp", "ArrowLeft"].includes(ev.key)) {
            ev.preventDefault();
            if (!list.length) {
                return;
            }
            this.state.highlightedProductIndex = Math.max(
                this.state.highlightedProductIndex - 1,
                0
            );
        } else if (ev.key === "Enter") {
            // Si no se movió con las flechas pero la búsqueda ya dejó
            // un único resultado, Enter lo agrega directo (para no
            // obligar a bajar con la flecha cuando ya está clarísimo
            // cuál es).
            const index =
                this.state.highlightedProductIndex >= 0
                    ? this.state.highlightedProductIndex
                    : list.length === 1
                    ? 0
                    : -1;
            if (index === -1 || !list[index]) {
                return; // deja que el buscador de más resultados de siempre actúe
            }
            ev.preventDefault();
            this.addProductToOrder(list[index]);
            this.state.highlightedProductIndex = -1;
        }
    },
});
