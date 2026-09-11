# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
from odoo import _, fields, models
from odoo.exceptions import UserError

from .taxxa_client import TaxxaClient


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_co_taxxa_base_url = fields.Char(
        string='URL de la API TAXXA',
        help="URL única que TAXXA asigna a esta cuenta. NO es la misma para todos los "
             "clientes de TAXXA — pídela a tu contacto comercial/técnico junto con las "
             "credenciales. La de los manuales públicos (taxxaapi.com/api.djson?demo1) "
             "es solo de demostración genérica.")
    l10n_co_taxxa_email = fields.Char(string='Usuario TAXXA (correo)')
    l10n_co_taxxa_password = fields.Char(string='Clave TAXXA')
    l10n_co_taxxa_environment = fields.Selection(
        [('test', 'Pruebas'), ('prod', 'Producción')],
        string='Ambiente TAXXA', default='test',
        help="TAXXA distingue ambiente de pruebas y producción tanto en el token como "
             "en el envío de documentos (wEnviroment). Empezar siempre en Pruebas.")
    l10n_co_taxxa_account = fields.Char(string='Cuenta TAXXA', readonly=True,
        help="Número de cuenta que devuelve TAXXA al generar el token (raccount).")
    l10n_co_taxxa_token = fields.Char(string='Token TAXXA', readonly=True, copy=False)
    l10n_co_taxxa_token_date = fields.Datetime(string='Token generado el', readonly=True, copy=False,
        help="TAXXA recomienda renovar el token cada 15 días — no dejarlo fijo indefinidamente.")

    def action_test_taxxa_connection(self):
        """Botón "Probar conexión" — valida las credenciales contra el
        ambiente real de TAXXA pidiendo un token, y lo guarda si
        funciona. No envía ningún documento fiscal, es solo la
        autenticación (la única parte de la API cuya respuesta está
        confirmada en la documentación pública)."""
        self.ensure_one()
        if not self.l10n_co_taxxa_email or not self.l10n_co_taxxa_password:
            raise UserError(_("Completa el usuario y la clave de TAXXA antes de probar la conexión."))
        client = TaxxaClient(self.l10n_co_taxxa_base_url)
        account, token = client.get_token(self.l10n_co_taxxa_email, self.l10n_co_taxxa_password)
        self.write({
            'l10n_co_taxxa_account': account,
            'l10n_co_taxxa_token': token,
            'l10n_co_taxxa_token_date': fields.Datetime.now(),
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Conexión con TAXXA exitosa"),
                'message': _("Cuenta %s — token guardado.", account),
                'type': 'success',
                'sticky': False,
            },
        }
