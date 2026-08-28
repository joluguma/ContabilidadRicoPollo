# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _run_wkhtmltopdf(self, *args, **kwargs):
        """wkhtmltopdf no tiene versión nativa para Apple Silicon — en
        este Mac corre traducido con Rosetta 2, lo que provoca fallas
        intermitentes con código -11 (segfault) bajo carga normal.
        Confirmado: la MISMA factura genera el PDF bien al reintentar
        de inmediato — no es un problema de los datos ni de la
        plantilla. En un servidor Linux real (producción) wkhtmltopdf
        corre nativo y esto no debería volver a aparecer.

        Mientras tanto, se reintenta automáticamente para que el
        usuario no tenga que darle "Imprimir" de nuevo a mano."""
        last_error = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return super()._run_wkhtmltopdf(*args, **kwargs)
            except UserError as exc:
                if 'Wkhtmltopdf failed' not in str(exc):
                    raise
                last_error = exc
                _logger.warning(
                    'wkhtmltopdf falló (intento %s/%s), reintentando automáticamente: %s',
                    attempt, MAX_ATTEMPTS, exc,
                )
        raise last_error
