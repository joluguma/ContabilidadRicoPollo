# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    piko_riko_inventory_value = fields.Monetary(
        string='Valor de inventario',
        currency_field='currency_id',
        compute='_compute_piko_riko_inventory_value',
        help="Cantidad a la mano x Costo. Para que este número sea real, "
             "primero hace falta el conteo físico (cargar la cantidad real "
             "de cada producto) — mientras eso no esté hecho, este valor "
             "solo refleja los productos que ya tienen cantidad cargada.",
    )

    @api.depends('qty_available', 'standard_price')
    def _compute_piko_riko_inventory_value(self):
        for product in self:
            product.piko_riko_inventory_value = product.qty_available * product.standard_price
