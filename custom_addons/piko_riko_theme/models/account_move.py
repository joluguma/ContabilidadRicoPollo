# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
import base64
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _piko_qr_data_uri(self, value, width=120, height=120):
        """Devuelve un código QR ya codificado como data URI (base64), listo
        para usar en <img src="...">, generado con el mismo motor nativo de
        Odoo (reportlab) que usa el controlador /report/barcode.

        Se genera en memoria en vez de pedirle al PDF que descargue la
        imagen por HTTP (como haría un <img src="/report/barcode/..."/>)
        para no depender de que wkhtmltopdf pueda resolver esa URL interna,
        y para no tener que codificar manualmente valores con espacios o
        tildes en una ruta de URL.

        IMPORTANTE: este QR es solo un identificador visual (nombre del
        cliente, a pedido explícito del cliente, nunca su cédula/NIT) — NO
        es ni reemplaza el QR fiscal de una factura electrónica real, que
        este sistema todavía no puede emitir (sin habilitación DIAN).
        """
        if not value:
            return ''
        try:
            png = self.env['ir.actions.report'].barcode(
                'QR', value, width=width, height=height)
            return 'data:image/png;base64,%s' % base64.b64encode(png).decode()
        except (ValueError, AttributeError) as e:
            _logger.warning('No se pudo generar el QR de referencia: %s', e)
            return ''
