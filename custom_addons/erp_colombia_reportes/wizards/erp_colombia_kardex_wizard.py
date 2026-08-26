# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo import fields, models
from odoo.tools import float_is_zero


class ErpColombiaKardexWizard(models.TransientModel):
    _name = 'erp.colombia.kardex.wizard'
    _description = 'ERP Colombia - Asistente de Kardex'

    company_id = fields.Many2one(
        'res.company', string='Compañía', required=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    product_id = fields.Many2one(
        'product.product', string='Producto', required=True,
        domain="[('is_storable', '=', True)]")
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Bodega',
        domain="[('company_id', '=', company_id)]",
        help='Déjelo vacío para consolidar todas las bodegas de la compañía.')
    date_from = fields.Date(
        string='Desde', required=True,
        default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Hasta', required=True, default=fields.Date.today)
    line_ids = fields.One2many(
        'erp.colombia.kardex.line', 'wizard_id', string='Movimientos', readonly=True)
    saldo_inicial_cantidad = fields.Float(string='Saldo inicial (cant.)', readonly=True)
    saldo_inicial_valor = fields.Monetary(
        string='Saldo inicial (valor)', readonly=True, currency_field='currency_id')

    def _moves_domain(self):
        self.ensure_one()
        domain = [
            ('product_id', '=', self.product_id.id),
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'done'),
            '|', ('is_in', '=', True), ('is_out', '=', True),
        ]
        if self.warehouse_id:
            domain.append(('picking_type_id.warehouse_id', '=', self.warehouse_id.id))
        return domain

    def _move_type_label(self, move):
        if move.picking_type_id:
            return move.picking_type_id.name
        if move.is_in:
            return 'Ajuste - Entrada'
        return 'Ajuste - Salida'

    def button_generate(self):
        self.ensure_one()
        self.line_ids.unlink()
        move_model = self.env['stock.move']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        previous_moves = move_model.search(
            self._moves_domain() + [('date', '<', self.date_from)],
            order='date, id',
        )
        saldo_cantidad = sum(
            m.quantity if m.is_in else -m.quantity for m in previous_moves)
        saldo_valor = sum(previous_moves.mapped('value'))
        self.saldo_inicial_cantidad = saldo_cantidad
        self.saldo_inicial_valor = saldo_valor

        moves = move_model.search(
            self._moves_domain() + [
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
            ],
            order='date, id',
        )

        line_vals = []
        for move in moves:
            entrada = move.quantity if move.is_in else 0.0
            salida = move.quantity if move.is_out else 0.0
            saldo_cantidad += entrada - salida
            saldo_valor += move.value
            costo_unitario = (
                abs(move.value) / move.quantity
                if not float_is_zero(move.quantity, precision_digits=precision)
                else 0.0
            )
            line_vals.append((0, 0, {
                'wizard_id': self.id,
                'date': move.date,
                'document': move.reference or move.name,
                'move_type': self._move_type_label(move),
                'entrada': entrada,
                'salida': salida,
                'saldo_cantidad': saldo_cantidad,
                'costo_unitario': costo_unitario,
                'costo_total': abs(move.value),
                'saldo_valor': saldo_valor,
                'warehouse': (
                    move.picking_type_id.warehouse_id.name
                    if move.picking_type_id.warehouse_id else ''
                ),
            }))
        self.line_ids = line_vals
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'erp.colombia.kardex.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def action_export_xlsx(self):
        self.ensure_one()
        return self.env.ref(
            'erp_colombia_reportes.action_report_erp_colombia_kardex_xlsx'
        ).report_action(self)


class ErpColombiaKardexLine(models.TransientModel):
    _name = 'erp.colombia.kardex.line'
    _description = 'ERP Colombia - Línea de Kardex'
    _order = 'date, id'

    wizard_id = fields.Many2one('erp.colombia.kardex.wizard', ondelete='cascade')
    currency_id = fields.Many2one(related='wizard_id.currency_id')
    date = fields.Datetime(string='Fecha')
    document = fields.Char(string='Documento')
    move_type = fields.Char(string='Tipo de movimiento')
    entrada = fields.Float(string='Entrada')
    salida = fields.Float(string='Salida')
    saldo_cantidad = fields.Float(string='Saldo')
    costo_unitario = fields.Monetary(string='Costo unitario', currency_field='currency_id')
    costo_total = fields.Monetary(string='Costo total', currency_field='currency_id')
    saldo_valor = fields.Monetary(string='Saldo (valor)', currency_field='currency_id')
    warehouse = fields.Char(string='Bodega')
