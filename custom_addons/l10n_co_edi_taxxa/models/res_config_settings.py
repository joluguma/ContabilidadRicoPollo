# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_co_taxxa_base_url = fields.Char(related='company_id.l10n_co_taxxa_base_url', readonly=False)
    l10n_co_taxxa_email = fields.Char(related='company_id.l10n_co_taxxa_email', readonly=False)
    l10n_co_taxxa_password = fields.Char(related='company_id.l10n_co_taxxa_password', readonly=False)
    l10n_co_taxxa_environment = fields.Selection(related='company_id.l10n_co_taxxa_environment', readonly=False)
    l10n_co_taxxa_account = fields.Char(related='company_id.l10n_co_taxxa_account')
    l10n_co_taxxa_token_date = fields.Datetime(related='company_id.l10n_co_taxxa_token_date')

    def action_test_taxxa_connection(self):
        return self.company_id.action_test_taxxa_connection()
