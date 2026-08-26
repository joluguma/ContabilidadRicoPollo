# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
import logging
from contextlib import contextmanager

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ErpColombiaDemoCleanupWizard(models.TransientModel):
    _name = 'erp.colombia.demo.cleanup.wizard'
    _description = 'ERP Colombia - Eliminar datos DEMO'

    batch_ids = fields.Many2many('erp.colombia.demo.batch', string='Lotes a eliminar')
    confirm = fields.Boolean(
        string='Entiendo que esto elimina permanentemente los datos de estos lotes DEMO')

    def button_cleanup(self):
        self.ensure_one()
        if not self.confirm:
            raise UserError(self.env._(
                'Debes marcar la casilla de confirmación antes de eliminar.'))
        if not self.batch_ids:
            raise UserError(self.env._('Selecciona al menos un lote.'))

        for batch in self.batch_ids:
            self._cleanup_batch(batch)
        return True

    @contextmanager
    def _try(self, label):
        """Si lo que hay dentro falla, revierte solo esa operación
        (SAVEPOINT) y sigue con el resto — un registro que no se puede
        borrar no debe abortar toda la transacción de limpieza."""
        try:
            with self.env.cr.savepoint():
                yield
        except Exception as e:  # noqa: BLE001
            _logger.warning('Limpieza DEMO — %s: %s', label, e)

    def _cleanup_batch(self, batch):
        partners = batch.partner_ids
        products = batch.product_tmpl_ids.mapped('product_variant_ids')
        n_partners_before, n_products_before = len(partners), len(products)

        # Asistentes transitorios (account.payment.register) que puedan
        # haber quedado con referencia a un partner DEMO.
        wiz_regs = self.env['account.payment.register'].search(
            [('partner_id', 'in', partners.ids)])
        with self._try('asistentes de pago pendientes'):
            wiz_regs.sudo().unlink()

        # Los pagos (account.payment) envuelven su propio account.move y
        # bloquean con RESTRICT el borrado del partner/move si se intenta
        # al revés: hay que borrarlos primero.
        payments = self.env['account.payment'].search([('partner_id', 'in', partners.ids)])
        for payment in payments:
            with self._try(f'pago {payment.name}'):
                if payment.state == 'paid':
                    payment.action_draft()
                if payment.state != 'cancel':
                    payment.action_cancel()
                payment.unlink()

        moves = self.env['account.move'].search([
            '|', ('partner_id', 'in', partners.ids),
            ('invoice_line_ids.product_id', 'in', products.ids),
        ])
        for move in moves:
            with self._try(f'account.move {move.name}'):
                if move.state == 'posted':
                    move.button_draft()
                if move.state != 'cancel':
                    move.button_cancel()
                move.unlink()

        for order_model in ('sale.order', 'purchase.order'):
            orders = self.env[order_model].search([('partner_id', 'in', partners.ids)])
            for order in orders:
                with self._try(f'movimientos de {order.name}'):
                    for picking in order.picking_ids:
                        if picking.state not in ('done', 'cancel'):
                            picking.action_cancel()
                        picking.unlink()
                with self._try(f'orden {order.name}'):
                    order.unlink()

        # Movimientos de inventario sueltos (ej. el ajuste de existencia
        # inicial) que no cuelgan de ningún picking de compra/venta.
        stray_moves = self.env['stock.move'].search([('product_id', 'in', products.ids)])
        for move in stray_moves:
            with self._try(f'movimiento de stock de {move.product_id.display_name}'):
                move.move_line_ids.unlink()
                move.unlink()

        quants = self.env['stock.quant'].search([('product_id', 'in', products.ids)])
        for quant in quants:
            with self._try(f'quant de {quant.product_id.display_name}'):
                quant.sudo().unlink()

        with self._try('productos DEMO'):
            products.mapped('product_tmpl_id').unlink()
        with self._try('terceros DEMO'):
            partners.unlink()

        n_partners_left = self.env['res.partner'].search_count(
            [('id', 'in', partners.ids)])
        n_products_left = self.env['product.product'].search_count(
            [('id', 'in', products.ids)])
        summary = (
            f'\n[Limpieza de {batch.name}] '
            f'Terceros eliminados: {n_partners_before - n_partners_left}/'
            f'{n_partners_before}. Productos eliminados: '
            f'{n_products_before - n_products_left}/{n_products_before}.'
        )
        if n_partners_left or n_products_left:
            summary += (
                ' Algunos no se pudieron eliminar porque tienen movimientos '
                'de inventario "hechos" (inmutables por diseño de Odoo) u '
                'otras referencias — revisar el log de warnings. Para un '
                'reset 100% garantizado, ver README.md: borrar y recrear la '
                'base de datos DEMO.'
            )
        batch.write({'state': 'draft', 'log': (batch.log or '') + summary})
