# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    erp_colombia_demo_batch_id = fields.Many2one(
        'erp.colombia.demo.batch', string='Lote DEMO', index=True, copy=False,
        help='Si tiene valor, este contacto fue generado por el motor de '
             'datos DEMO y puede eliminarse de forma segura junto con su lote.')
