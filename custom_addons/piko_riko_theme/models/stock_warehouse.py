# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    # Expone en la bodega misma la nota que ya se guarda en el contacto
    # de la bodega (partner_id.comment) — se cargó ahí para las bodegas
    # reales (ver scripts/crear_bodegas.py) porque stock.warehouse no
    # tiene un campo de texto libre nativo. related=... con
    # readonly=False permite verla y editarla directo desde la bodega,
    # sin tener que entrar al contacto.
    piko_riko_observaciones = fields.Html(
        string='Observaciones',
        related='partner_id.comment',
        readonly=False,
    )
