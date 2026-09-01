# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
from datetime import timedelta

from odoo import api, fields, models


class PikoRikoDashboard(models.AbstractModel):
    _name = 'piko.riko.dashboard'
    _description = 'Piko Riko - KPIs del dashboard'

    @api.model
    def _sales_total(self, date_from, date_to, company):
        """Ventas confirmadas (cotizaciones convertidas en pedido) más
        ventas de punto de venta pagadas, en [date_from, date_to)."""
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
    def _pct_change(self, current, previous):
        if not previous:
            return None
        return round((current - previous) / previous * 100, 1)

    @api.model
    def get_kpis(self):
        company = self.env.company
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        prev_month_end = month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)
        # Se compara el mes en curso (a la fecha) contra el MISMO tramo
        # de días del mes anterior, no el mes anterior completo — así la
        # variación no es engañosa a mitad de mes.
        days_elapsed = (today - month_start).days
        prev_comparable_end = min(prev_month_start + timedelta(days=days_elapsed), prev_month_end)

        ventas_dia = self._sales_total(today, today + timedelta(days=1), company)
        ventas_mes = self._sales_total(month_start, today + timedelta(days=1), company)
        ventas_mes_prev = self._sales_total(
            prev_month_start, prev_comparable_end + timedelta(days=1), company)

        purchases = self.env['purchase.order'].search([
            ('state', 'in', ('purchase', 'done')),
            ('date_order', '>=', month_start),
            ('company_id', '=', company.id),
        ])
        compras_mes = sum(purchases.mapped('amount_total'))

        receivable_moves = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', company.id),
        ])
        payable_moves = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', company.id),
        ])

        pedidos_pendientes = self.env['sale.order'].search_count([
            ('state', '=', 'sale'),
            ('invoice_status', '!=', 'invoiced'),
            ('company_id', '=', company.id),
        ])

        storable = self.env['product.template'].search([
            ('is_storable', '=', True),
            ('company_id', 'in', (company.id, False)),
        ])
        inventario_disponible = sum(storable.mapped('qty_available'))
        valor_inventario = sum(
            p.qty_available * p.standard_price for p in storable
        )

        stock_bajo = 0
        if 'stock.warehouse.orderpoint' in self.env:
            for orderpoint in self.env['stock.warehouse.orderpoint'].search(
                    [('company_id', '=', company.id)]):
                if orderpoint.product_id.qty_available <= orderpoint.product_min_qty:
                    stock_bajo += 1

        return {
            'moneda_simbolo': company.currency_id.symbol or '$',
            'ventas_dia': ventas_dia,
            'ventas_mes': ventas_mes,
            'ventas_mes_variacion_pct': self._pct_change(ventas_mes, ventas_mes_prev),
            'compras_mes': compras_mes,
            'inventario_disponible': inventario_disponible,
            'valor_inventario': valor_inventario,
            'stock_bajo': stock_bajo,
            'cuentas_por_cobrar': sum(receivable_moves.mapped('amount_residual')),
            'cuentas_por_pagar': sum(payable_moves.mapped('amount_residual')),
            'utilidad_mes': ventas_mes - compras_mes,
            'facturas_pendientes': len(receivable_moves),
            'pedidos_pendientes': pedidos_pendientes,
        }
