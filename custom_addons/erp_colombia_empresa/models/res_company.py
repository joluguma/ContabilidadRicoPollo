# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # res.company ya no delega en res.partner por _inherits (a diferencia de
    # versiones anteriores de Odoo): hay que exponer los campos explícitamente
    # como `related`, igual que hace l10n_co_electronic_invoice (OCA) con sus
    # propios campos de regimen fiscal/CIIU.
    trade_name = fields.Char(
        related='partner_id.trade_name', readonly=False, string='Nombre comercial')
    l10n_co_verification_digit = fields.Char(
        related='partner_id.l10n_co_verification_digit', string='DV')
