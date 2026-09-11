# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
from datetime import timedelta

from odoo import api, fields, models


class PikoRikoDashboard(models.AbstractModel):
    _name = 'piko.riko.dashboard'
    _description = 'Piko Riko - Datos del dashboard'

    # ------------------------------------------------------------------
    # Rango de fechas según el período elegido en el dashboard
    # ------------------------------------------------------------------
    @api.model
    def _period_range(self, period):
        """Devuelve (inicio, fin, inicio_prev, fin_prev) para comparar
        contra el período anterior equivalente."""
        today = fields.Date.context_today(self)
        if period == 'today':
            start = today
            end = today + timedelta(days=1)
            prev_start = today - timedelta(days=1)
            prev_end = today
        elif period == 'week':
            start = today - timedelta(days=today.weekday())
            end = today + timedelta(days=1)
            prev_start = start - timedelta(days=7)
            prev_end = prev_start + (today - start) + timedelta(days=1)
        elif period == 'year':
            start = today.replace(month=1, day=1)
            end = today + timedelta(days=1)
            prev_start = start.replace(year=start.year - 1)
            days_elapsed = (today - start).days
            prev_end = prev_start + timedelta(days=days_elapsed + 1)
        else:  # month (por defecto)
            start = today.replace(day=1)
            end = today + timedelta(days=1)
            prev_month_end = start - timedelta(days=1)
            prev_start = prev_month_end.replace(day=1)
            days_elapsed = (today - start).days
            prev_end = min(prev_start + timedelta(days=days_elapsed), prev_month_end) + timedelta(days=1)
        return start, end, prev_start, prev_end

    @api.model
    def _sales_total(self, date_from, date_to, company):
        orders = self.env['sale.order'].search([
            ('state', '=', 'sale'),
            ('date_order', '>=', date_from),
            ('date_order', '<', date_to),
            ('company_id', '=', company.id),
        ])
        total = sum(orders.mapped('amount_total'))
        if 'pos.order' in self.env:
            pos_orders = self.env['pos.order'].search([
                ('state', 'in', ('paid', 'done', 'invoiced')),
                ('date_order', '>=', date_from),
                ('date_order', '<', date_to),
                ('company_id', '=', company.id),
            ])
            total += sum(pos_orders.mapped('amount_total'))
        return total

    @api.model
    def _purchases_total(self, date_from, date_to, company):
        purchases = self.env['purchase.order'].search([
            ('state', 'in', ('purchase', 'done')),
            ('date_order', '>=', date_from),
            ('date_order', '<', date_to),
            ('company_id', '=', company.id),
        ])
        return sum(purchases.mapped('amount_total'))

    @api.model
    def _pct_change(self, current, previous):
        if not previous:
            return None
        return round((current - previous) / previous * 100, 1)

    # ------------------------------------------------------------------
    # Datos del dashboard: KPIs + alertas + actividad reciente
    # ------------------------------------------------------------------
    @api.model
    def get_dashboard_data(self, period='month'):
        company = self.env.company
        today = fields.Date.context_today(self)
        start, end, prev_start, prev_end = self._period_range(period)

        ventas = self._sales_total(start, end, company)
        ventas_prev = self._sales_total(prev_start, prev_end, company)
        compras = self._purchases_total(start, end, company)
        compras_prev = self._purchases_total(prev_start, prev_end, company)

        receivable = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', company.id),
        ])
        payable = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', company.id),
        ])
        cartera_vencida = receivable.filtered(
            lambda m: m.invoice_date_due and m.invoice_date_due < today)

        storable = self.env['product.template'].search([
            ('is_storable', '=', True),
            ('company_id', 'in', (company.id, False)),
        ])
        valor_inventario = sum(p.qty_available * p.standard_price for p in storable)

        stock_bajo = 0
        if 'stock.warehouse.orderpoint' in self.env:
            for op in self.env['stock.warehouse.orderpoint'].search(
                    [('company_id', '=', company.id)]):
                if op.product_id.qty_available <= op.product_min_qty:
                    stock_bajo += 1

        pedidos_pendientes = self.env['sale.order'].search_count([
            ('state', '=', 'sale'),
            ('invoice_status', '!=', 'invoiced'),
            ('company_id', '=', company.id),
        ])

        kpis = {
            'moneda': company.currency_id.symbol or '$',
            'ventas': ventas,
            'ventas_var': self._pct_change(ventas, ventas_prev),
            'compras': compras,
            'compras_var': self._pct_change(compras, compras_prev),
            'utilidad': ventas - compras,
            'valor_inventario': valor_inventario,
            'cuentas_por_cobrar': sum(receivable.mapped('amount_residual')),
            'cuentas_por_pagar': sum(payable.mapped('amount_residual')),
            'facturas_pendientes': len(receivable),
            'pedidos_pendientes': pedidos_pendientes,
            'stock_bajo': stock_bajo,
        }

        alertas = []
        if stock_bajo:
            alertas.append({
                'key': 'stock_bajo',
                'titulo': 'Stock bajo',
                'detalle': '%d producto(s) por debajo del mínimo' % stock_bajo,
            })
        if receivable:
            alertas.append({
                'key': 'facturas_pendientes',
                'titulo': 'Facturas por cobrar',
                'detalle': '%d documento(s) sin pagar' % len(receivable),
            })
        if cartera_vencida:
            alertas.append({
                'key': 'cartera_vencida',
                'titulo': 'Cartera vencida',
                'detalle': '%s %s en %d factura(s)' % (
                    company.currency_id.symbol or '$',
                    '{:,.0f}'.format(sum(cartera_vencida.mapped('amount_residual'))).replace(',', '.'),
                    len(cartera_vencida)),
            })

        return {
            'kpis': kpis,
            'alertas': alertas,
            'actividad': self._recent_activity(company),
        }

    @api.model
    def _recent_activity(self, company):
        items = []

        tipos_factura = {
            'out_invoice': 'Factura',
            'in_invoice': 'Factura de compra',
            'out_refund': 'Nota de crédito',
            'in_refund': 'Nota de débito recibida',
            'entry': 'Asiento',
        }
        for m in self.env['account.move'].search(
                [('company_id', '=', company.id), ('state', '=', 'posted')],
                order='write_date desc', limit=6):
            items.append({
                'icon': 'fa-file-text-o',
                'texto': '%s %s' % (tipos_factura.get(m.move_type, 'Documento'), m.name),
                'usuario': m.write_uid.name,
                'fecha': fields.Datetime.to_string(m.write_date),
            })

        for po in self.env['purchase.order'].search(
                [('company_id', '=', company.id), ('state', 'in', ('purchase', 'done'))],
                order='write_date desc', limit=4):
            items.append({
                'icon': 'fa-truck',
                'texto': 'Orden de compra %s — %s' % (po.name, po.partner_id.name or ''),
                'usuario': po.write_uid.name,
                'fecha': fields.Datetime.to_string(po.write_date),
            })

        if 'stock.picking' in self.env:
            for pk in self.env['stock.picking'].search(
                    [('company_id', '=', company.id), ('state', '=', 'done')],
                    order='write_date desc', limit=4):
                items.append({
                    'icon': 'fa-cubes',
                    'texto': 'Movimiento de inventario %s' % pk.name,
                    'usuario': pk.write_uid.name,
                    'fecha': fields.Datetime.to_string(pk.write_date),
                })

        items.sort(key=lambda x: x['fecha'] or '', reverse=True)
        return items[:8]
