# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
import base64
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_pdf(self):
        """Fase 17: el botón "Imprimir" de la factura debe abrir de una vez
        la tirilla (es el formato que realmente se usa día a día en la
        caja), no la factura A4 estándar — eso confundía al usuario, que
        esperaba ver la tirilla con el QR y en cambio se le descargaba el
        PDF normal en inglés.

        Ojo: esto NO toca el botón "Enviar" (correo) — ese sigue adjuntando
        la factura A4 estándar, que es el formato correcto para un archivo
        adjunto de correo (la tirilla es angosta, pensada para papel
        térmico, no para verse en pantalla).
        """
        self.ensure_one()
        if self.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
            # OJO: se devuelve la acción PDF normal (report_type='qweb-pdf'),
            # NO la de "impresión directa" — es el handler JS
            # (tirilla_direct_print.js, en el punto de extensión
            # "ir.actions.report handlers") el que la intercepta y la
            # convierte en la apertura directa del diálogo de imprimir.
            # Devolver acá la acción qweb-html directamente NO logra lo
            # mismo: Odoo la muestra en una vista embebida con su propio
            # botón "Imprimir" que, irónicamente, sigue descargando el PDF.
            report = self.env.ref(
                'piko_riko_theme.action_report_invoice_receipt', raise_if_not_found=False)
            if report:
                return report.report_action(self.id, config=False)
        return super().action_print_pdf()

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
