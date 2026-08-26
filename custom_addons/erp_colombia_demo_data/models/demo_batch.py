# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
"""Motor de generación de datos DEMO para ERP Colombia.

No crea ningún modelo de negocio nuevo: reutiliza sale/purchase/stock/
account tal cual. Ver README.md para las decisiones de diseño (por qué
vive en una base de datos separada, por qué ALLOW_REAL_DIAN es una
constante y no un campo, etc.).
"""
import logging
import random
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)

try:
    from faker import Faker
except ImportError:  # pragma: no cover - se valida en tiempo de ejecución
    Faker = None

# Protección explícita pedida por el prompt maestro: nunca se convierte
# en True en tiempo de ejecución, no es un campo editable desde la UI.
ALLOW_REAL_DIAN = False

CATEGORY_NAMES = [
    'Alimentos', 'Bebidas', 'Tecnología', 'Papelería', 'Hogar',
    'Servicios', 'Repuestos', 'Ropa', 'Aseo', 'Otros',
]
WAREHOUSE_NAMES = [
    'Bodega Principal', 'Bodega Norte', 'Bodega Sur', 'Bodega Popayán',
    'Bodega Cali', 'Bodega Bogotá', 'Bodega Distribución', 'Bodega Devoluciones',
]
CREDIT_NOTE_REASONS = [
    'Devolución completa', 'Devolución parcial', 'Descuento posterior',
    'Corrección de factura',
]

MODE_PRESETS = {
    'small': dict(
        n_clientes=50, n_proveedores=20, n_empresas=10, n_productos=50,
        n_categorias=10, n_bodegas=3, n_cotizaciones=100, n_pedidos=80,
        n_ordenes_compra=100, n_notas_credito=10, n_pagos_recibidos=80,
        n_pagos_realizados=80, dian_sample_size=5,
    ),
    'standard': dict(
        n_clientes=1000, n_proveedores=300, n_empresas=50, n_productos=1000,
        n_categorias=50, n_bodegas=20, n_cotizaciones=1000, n_pedidos=2000,
        n_ordenes_compra=1000, n_notas_credito=300, n_pagos_recibidos=2000,
        n_pagos_realizados=1000, dian_sample_size=20,
    ),
    'stress': dict(
        n_clientes=10000, n_proveedores=5000, n_empresas=200, n_productos=10000,
        n_categorias=100, n_bodegas=30, n_cotizaciones=20000, n_pedidos=50000,
        n_ordenes_compra=20000, n_notas_credito=2000, n_pagos_recibidos=50000,
        n_pagos_realizados=20000, dian_sample_size=20,
    ),
}

COMMIT_EVERY = 200


class ErpColombiaDemoBatch(models.Model):
    _name = 'erp.colombia.demo.batch'
    _description = 'ERP Colombia - Lote de datos DEMO'
    _order = 'id desc'

    name = fields.Char(default='Nuevo lote DEMO', readonly=True)
    seed = fields.Integer(string='Semilla (DEMO_SEED)', required=True, default=20260825)
    mode = fields.Selection([
        ('small', 'SMALL'), ('standard', 'STANDARD'),
        ('stress', 'STRESS'), ('custom', 'CUSTOM'),
    ], default='small', required=True)
    state = fields.Selection([
        ('draft', 'Borrador'), ('running', 'Generando'),
        ('done', 'Completado'), ('error', 'Error'),
    ], default='draft', readonly=True, copy=False)

    date_from = fields.Date(default=lambda self: fields.Date.today() - timedelta(days=180))
    date_to = fields.Date(default=fields.Date.today)
    pct_venta_contado = fields.Float(string='% ventas de contado', default=40.0)
    pct_compra_contado = fields.Float(string='% compras de contado', default=30.0)

    n_clientes = fields.Integer(string='Clientes', default=50)
    n_proveedores = fields.Integer(string='Proveedores', default=20)
    n_empresas = fields.Integer(
        string='Empresas (persona jurídica) entre los clientes', default=10)
    n_productos = fields.Integer(string='Productos', default=50)
    n_categorias = fields.Integer(string='Categorías', default=10)
    n_bodegas = fields.Integer(string='Bodegas', default=3)
    n_cotizaciones = fields.Integer(string='Cotizaciones', default=100)
    n_pedidos = fields.Integer(string='Pedidos confirmados', default=80)
    n_ordenes_compra = fields.Integer(string='Órdenes de compra', default=100)
    n_notas_credito = fields.Integer(string='Notas crédito', default=10)
    n_pagos_recibidos = fields.Integer(string='Pagos recibidos (máx.)', default=80)
    n_pagos_realizados = fields.Integer(string='Pagos realizados (máx.)', default=80)
    dian_sample_size = fields.Integer(
        string='Facturas a probar con DIAN demo', default=5,
        help='Solo esta cantidad de facturas de venta pasa por la generación '
             'real de XML/CUFE (firma incluida): hacerlo para miles de '
             'facturas sería lento e innecesario para datos de prueba.')

    created_clientes = fields.Integer(readonly=True, copy=False)
    created_proveedores = fields.Integer(readonly=True, copy=False)
    created_productos = fields.Integer(readonly=True, copy=False)
    created_bodegas = fields.Integer(readonly=True, copy=False)
    created_cotizaciones = fields.Integer(readonly=True, copy=False)
    created_pedidos = fields.Integer(readonly=True, copy=False)
    created_facturas_venta = fields.Integer(readonly=True, copy=False)
    created_notas_credito = fields.Integer(readonly=True, copy=False)
    created_ordenes_compra = fields.Integer(readonly=True, copy=False)
    created_facturas_compra = fields.Integer(readonly=True, copy=False)
    created_pagos = fields.Integer(readonly=True, copy=False)
    created_facturas_dian = fields.Integer(readonly=True, copy=False)

    start_datetime = fields.Datetime(readonly=True, copy=False)
    end_datetime = fields.Datetime(readonly=True, copy=False)
    log = fields.Text(readonly=True, copy=False)
    error_message = fields.Text(readonly=True, copy=False)
    validation_report = fields.Text(readonly=True, copy=False)
    validation_ok = fields.Boolean(readonly=True, copy=False)

    partner_ids = fields.One2many(
        'res.partner', 'erp_colombia_demo_batch_id', string='Terceros generados', readonly=True)
    product_tmpl_ids = fields.One2many(
        'product.template', 'erp_colombia_demo_batch_id', string='Productos generados', readonly=True)

    @api.onchange('mode')
    def _onchange_mode(self):
        preset = MODE_PRESETS.get(self.mode)
        if preset:
            self.update(preset)

    # ------------------------------------------------------------------
    # Orquestación
    # ------------------------------------------------------------------

    def _log(self, msg):
        _logger.info('[DEMO %s] %s', self.name or self.id, msg)
        self.log = (self.log or '') + msg + '\n'

    def button_generate(self):
        self.ensure_one()
        if Faker is None:
            raise UserError(self.env._(
                "Falta instalar la librería Python 'faker' (pip install Faker)."))
        if self.state == 'running':
            raise UserError(self.env._('Este lote ya se está generando.'))
        assert ALLOW_REAL_DIAN is False, (
            'ALLOW_REAL_DIAN debe permanecer en False: los datos DEMO nunca '
            'se envían a la DIAN real.')

        self.write({
            'name': f'DEMO-{fields.Datetime.now():%Y%m%d-%H%M%S}-seed{self.seed}',
            'state': 'running', 'start_datetime': fields.Datetime.now(), 'log': '',
        })
        # Commit necesario aquí (fuera de un test): si algo falla más
        # adelante y hacemos rollback, este registro debe sobrevivir para
        # poder reportar el error. Dentro de un test, Odoo bloquea
        # commit/rollback a propósito (TransactionCase) — _safe_commit lo
        # detecta y no hace nada, dejando todo en la transacción única del
        # test, que es exactamente lo que se quiere ahí.
        self._safe_commit()

        fake = Faker('es_CO')
        Faker.seed(self.seed)
        rng = random.Random(self.seed)

        try:
            self._ensure_company_setup()
            partners = self._generate_partners(fake, rng)
            products = self._generate_products(fake, rng)
            warehouses = self._generate_warehouses(fake, rng)
            self._generate_initial_stock(rng, products, warehouses)
            self._generate_purchases(rng, partners['proveedores'], products, warehouses)
            self._generate_sales(rng, partners['clientes'], products, warehouses)
            self._generate_credit_notes(rng)
            self._generate_payments(rng)
            self._run_validations()
            self.write({'state': 'done', 'end_datetime': fields.Datetime.now()})
            self._log('Generación completada.')
        except Exception as e:
            _logger.exception('Fallo generando el lote DEMO %s', self.name)
            self._safe_rollback()
            self.write({
                'state': 'error', 'error_message': str(e),
                'end_datetime': fields.Datetime.now(),
            })
        self._safe_commit()
        return True

    def _safe_commit(self):
        """Comitea, salvo dentro de un test (Odoo lo bloquea a propósito;
        ahí no hace falta: todo vive en la transacción única del test)."""
        try:
            self.env.cr.commit()
        except AssertionError:
            pass

    def _safe_rollback(self):
        try:
            self.env.cr.rollback()
        except AssertionError:
            pass

    def _checkpoint(self, i, total, label):
        if total and i and i % COMMIT_EVERY == 0:
            self._log(f'  {label}: {i}/{total}...')
            self._safe_commit()

    # ------------------------------------------------------------------
    # 0. Compañía
    # ------------------------------------------------------------------

    def _ensure_company_setup(self):
        company = self.env.company
        if company.country_id.code != 'CO':
            self._log('Configurando compañía como Colombia (país/moneda/PUC)...')
            company.write({
                'country_id': self.env.ref('base.co').id,
                'currency_id': self.env.ref('base.COP').id,
            })
            self.env['account.chart.template'].try_loading(
                'co', company, install_demo=False)
        else:
            self._log('Compañía ya configurada como Colombia, se reutiliza.')

    # ------------------------------------------------------------------
    # 1. Terceros (empresas + clientes + proveedores)
    # ------------------------------------------------------------------

    def _make_nit(self, rng, used_nits):
        from odoo.addons.erp_colombia_terceros.models.res_partner import (
            l10n_co_compute_verification_digit,
        )
        while True:
            nit = str(rng.randint(700000000, 899999999))
            if nit not in used_nits:
                used_nits.add(nit)
                dv = l10n_co_compute_verification_digit(nit)
                return f'{nit}-{dv}'

    def _generate_partners(self, fake, rng):
        self._log(f'Generando terceros: {self.n_clientes} clientes, '
                   f'{self.n_proveedores} proveedores ({self.n_empresas} '
                   f'de los clientes serán persona jurídica)...')
        co = self.env.ref('base.co')
        nit_type = self.env.ref('l10n_co.rut')
        cedula_type = self.env.ref('l10n_co.national_citizen_id')
        states = self.env['res.country.state'].search([('country_id', '=', co.id)])
        ciiu_codes = self.env['l10n_co.ciiu'].search([('is_code', '=', True)])
        used_nits = set()
        Partner = self.env['res.partner']

        clientes = Partner
        n_empresas = min(self.n_empresas, self.n_clientes)
        for i in range(self.n_clientes):
            is_company = i < n_empresas
            state = rng.choice(states) if states else False
            vals = {
                'erp_colombia_demo_batch_id': self.id,
                'is_company': is_company,
                'country_id': co.id,
                'state_id': state.id if state else False,
                'city': fake.city(),
                'email': fake.company_email() if is_company else fake.email(),
                'customer_rank': 1,
            }
            if is_company:
                vals.update({
                    'name': f'[DEMO] {fake.company()}',
                    'l10n_latam_identification_type_id': nit_type.id,
                    'vat': self._make_nit(rng, used_nits),
                    'l10n_co_ciiu_id': rng.choice(ciiu_codes).id if ciiu_codes else False,
                })
            else:
                vals.update({
                    'name': f'[DEMO] {fake.name()}',
                    'l10n_latam_identification_type_id': cedula_type.id,
                    'vat': str(rng.randint(10000000, 99999999)),
                })
            clientes += Partner.create(vals)
            self._checkpoint(i + 1, self.n_clientes, 'Clientes')
        self.created_clientes = len(clientes)

        proveedores = Partner
        for i in range(self.n_proveedores):
            state = rng.choice(states) if states else False
            proveedores += Partner.create({
                'erp_colombia_demo_batch_id': self.id,
                'name': f'[DEMO] {fake.company()} Proveedor',
                'is_company': True,
                'country_id': co.id,
                'state_id': state.id if state else False,
                'city': fake.city(),
                'email': fake.company_email(),
                'supplier_rank': 1,
                'l10n_latam_identification_type_id': nit_type.id,
                'vat': self._make_nit(rng, used_nits),
                'l10n_co_ciiu_id': rng.choice(ciiu_codes).id if ciiu_codes else False,
            })
            self._checkpoint(i + 1, self.n_proveedores, 'Proveedores')
        self.created_proveedores = len(proveedores)
        self._safe_commit()
        return {'clientes': clientes, 'proveedores': proveedores}

    # ------------------------------------------------------------------
    # 2. Productos y categorías
    # ------------------------------------------------------------------

    def _generate_products(self, fake, rng):
        self._log(f'Generando {self.n_categorias} categorías y '
                   f'{self.n_productos} productos...')
        Category = self.env['product.category']
        categories = Category
        for i in range(self.n_categorias):
            base_name = CATEGORY_NAMES[i % len(CATEGORY_NAMES)]
            name = base_name if i < len(CATEGORY_NAMES) else f'{base_name} {i}'
            cat = Category.create({
                'name': f'[DEMO#{self.id}] {name}',
                'property_valuation': 'real_time',
                'property_cost_method': 'average',
            })
            categories += cat

        company = self.env.company
        sale_tax = company.account_sale_tax_id
        purchase_tax = company.account_purchase_tax_id
        Product = self.env['product.product']
        products = Product
        for i in range(self.n_productos):
            category = rng.choice(categories)
            is_service = 'Servicios' in category.name
            cost = round(rng.uniform(5000, 300000), -2)
            price = round(cost * rng.uniform(1.2, 2.0), -2)
            vals = {
                'name': f'[DEMO#{self.id}] {fake.catch_phrase()} {i:05d}',
                'default_code': f'DEMO{self.id}-{i:05d}',
                'categ_id': category.id,
                'type': 'service' if is_service else 'consu',
                'is_storable': not is_service,
                'list_price': price,
                'standard_price': cost,
                'taxes_id': [(6, 0, sale_tax.ids)] if sale_tax else False,
                'supplier_taxes_id': [(6, 0, purchase_tax.ids)] if purchase_tax else False,
                'invoice_policy': 'order',
            }
            product_tmpl = Product.create(vals).product_tmpl_id
            product_tmpl.erp_colombia_demo_batch_id = self.id
            products += product_tmpl.product_variant_id
            self._checkpoint(i + 1, self.n_productos, 'Productos')
        self.created_productos = len(products)
        self._safe_commit()
        return products

    # ------------------------------------------------------------------
    # 3. Bodegas
    # ------------------------------------------------------------------

    def _generate_warehouses(self, fake, rng):
        self._log(f'Generando {self.n_bodegas} bodegas...')
        Warehouse = self.env['stock.warehouse']
        existing = Warehouse.search([('company_id', '=', self.env.company.id)])
        warehouses = existing
        for i in range(self.n_bodegas):
            base_name = WAREHOUSE_NAMES[i % len(WAREHOUSE_NAMES)]
            name = base_name if i < len(WAREHOUSE_NAMES) else f'{base_name} {i}'
            code = f'D{self.id}{i:02d}'[:5]
            warehouses += Warehouse.create({
                'name': f'[DEMO#{self.id}] {name}',
                'code': code,
            })
        self.created_bodegas = len(warehouses) - len(existing)
        return warehouses

    # ------------------------------------------------------------------
    # 4. Existencias iniciales (variadas: alto, bajo, agotado)
    # ------------------------------------------------------------------

    def _generate_initial_stock(self, rng, products, warehouses):
        self._log('Cargando existencias iniciales variadas por producto...')
        Quant = self.env['stock.quant']
        storable = products.filtered(lambda p: p.type == 'consu' and p.is_storable)
        for i, product in enumerate(storable):
            warehouse = rng.choice(warehouses)
            roll = rng.random()
            if roll < 0.10:
                qty = 0
            elif roll < 0.40:
                qty = rng.randint(1, 20)
            elif roll < 0.80:
                qty = rng.randint(21, 200)
            else:
                qty = rng.randint(201, 1000)
            if qty:
                quant = Quant.with_context(inventory_mode=True).create({
                    'product_id': product.id,
                    'location_id': warehouse.lot_stock_id.id,
                    'inventory_quantity': qty,
                })
                quant.action_apply_inventory()
            self._checkpoint(i + 1, len(storable), 'Existencias iniciales')
        self._safe_commit()

    # ------------------------------------------------------------------
    # 5. Compras: Proveedor -> Orden -> Recepción -> Factura -> CxP
    # ------------------------------------------------------------------

    def _random_date(self, rng):
        span = (self.date_to - self.date_from).days
        return self.date_from + timedelta(days=rng.randint(0, max(span, 0)))

    def _generate_purchases(self, rng, proveedores, products, warehouses):
        self._log(f'Generando {self.n_ordenes_compra} órdenes de compra...')
        purchasable = products.filtered(lambda p: p.type != 'service') or products
        PurchaseOrder = self.env['purchase.order']
        AccountMove = self.env['account.move']
        n_facturas = 0
        for i in range(self.n_ordenes_compra):
            if not proveedores or not purchasable:
                break
            partner = rng.choice(proveedores)
            date = self._random_date(rng)
            lines = []
            for _p in range(rng.randint(1, 5)):
                product = rng.choice(purchasable)
                qty = rng.randint(5, 100)
                lines.append((0, 0, {
                    'product_id': product.id,
                    'product_qty': qty,
                    'product_uom_id': product.uom_id.id,
                    'price_unit': product.standard_price,
                }))
            po = PurchaseOrder.create({
                'partner_id': partner.id,
                'date_order': date,
                'order_line': lines,
            })
            po.button_confirm()

            roll = rng.random()
            if roll < 0.10:
                self._checkpoint(i + 1, self.n_ordenes_compra, 'Órdenes de compra')
                continue  # sin recepción todavía (escenario "pendiente")

            picking = po.picking_ids and po.picking_ids[0]
            if picking:
                full = roll < 0.80
                for move in picking.move_ids:
                    qty = move.product_uom_qty if full else move.product_uom_qty * rng.uniform(0.3, 0.9)
                    move.write({'quantity': qty, 'picked': True})
                try:
                    picking.button_validate()
                except Exception as e:  # noqa: BLE001
                    self._log(f'  Aviso: recepción {po.name} no se pudo validar: {e}')

            if roll < 0.90:
                try:
                    action = po.action_create_invoice()
                    bill = AccountMove.browse(action['res_id'])
                    bill.invoice_date = date
                    bill.action_post()
                    n_facturas += 1
                except Exception as e:  # noqa: BLE001
                    self._log(f'  Aviso: factura de {po.name} no se pudo contabilizar: {e}')
            self._checkpoint(i + 1, self.n_ordenes_compra, 'Órdenes de compra')
        self.created_ordenes_compra = self.n_ordenes_compra
        self.created_facturas_compra = n_facturas
        self._safe_commit()

    # ------------------------------------------------------------------
    # 6. Ventas: Cliente -> Cotización -> Pedido -> Entrega -> Factura -> DIAN -> CxC
    # ------------------------------------------------------------------

    def _get_or_create_dian_journal(self):
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'), ('company_id', '=', self.env.company.id),
        ], limit=1)
        if journal and not journal.l10n_latam_use_documents:
            journal.write({
                'l10n_latam_use_documents': True,
                'l10n_co_dian_operation_mode': 'demo',
                'l10n_co_dian_resolution_type_test': 'FACTURA ELECTRÓNICA DE VENTA',
                'l10n_co_electronic_document_resolution_test': '000000000',
                # OJO: en modo demo/habilitación el módulo lee los campos
                # con sufijo _test para la numeración, no los normales
                # (esos solo se usan en modo producción) - bug real que
                # encontramos al probar esto (ver PORT_NOTES/README).
                'l10n_co_electronic_document_prefix_test': 'DEMO',
                'l10n_co_electronic_document_start_number_test': 1,
                'l10n_co_electronic_document_end_number_test': 5000000,
                'l10n_co_dian_software_identification':
                    '00000000-0000-0000-0000-000000000000',
                'l10n_co_dian_software_pin': '00000',
            })
        return journal

    def _generate_sales(self, rng, clientes, products, warehouses):
        # Un "pedido" es una cotización confirmada: no puede haber más
        # pedidos que cotizaciones. Si se pide lo contrario (como en el
        # preset STANDARD original: 1000 cotizaciones / 2000 pedidos),
        # se generan al menos tantas cotizaciones como pedidos pedidos,
        # en vez de truncar los pedidos en silencio.
        n_cotizaciones = max(self.n_cotizaciones, self.n_pedidos)
        self._log(f'Generando {n_cotizaciones} cotizaciones '
                   f'({self.n_pedidos} se confirmarán como pedido)...')
        sellable = products or self.env['product.product']
        SaleOrder = self.env['sale.order']
        journal = self._get_or_create_dian_journal()
        doc_type = self.env['l10n_latam.document.type'].search([
            ('code', '=', '01'), ('country_id.code', '=', 'CO'),
        ], limit=1)

        quotations = SaleOrder
        for i in range(n_cotizaciones):
            if not clientes or not sellable:
                break
            partner = rng.choice(clientes)
            date = self._random_date(rng)
            lines = []
            for _p in range(rng.randint(1, 5)):
                product = rng.choice(sellable)
                lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': rng.randint(1, 20),
                    'price_unit': product.list_price,
                }))
            so = SaleOrder.create({
                'partner_id': partner.id,
                'date_order': date,
                'order_line': lines,
            })
            quotations += so
            self._checkpoint(i + 1, n_cotizaciones, 'Cotizaciones')
        self.created_cotizaciones = len(quotations)
        self._safe_commit()

        target_confirm = min(self.n_pedidos, len(quotations))
        to_confirm = rng.sample(list(quotations.ids), target_confirm) if target_confirm else []
        n_facturas = 0
        n_dian = 0
        for i, so_id in enumerate(to_confirm):
            so = SaleOrder.browse(so_id)
            try:
                so.action_confirm()
            except Exception as e:  # noqa: BLE001
                self._log(f'  Aviso: {so.name} no se pudo confirmar: {e}')
                continue

            roll = rng.random()
            picking = so.picking_ids and so.picking_ids[0]
            if picking and roll >= 0.10:
                full = roll < 0.85
                for move in picking.move_ids:
                    qty = move.product_uom_qty if full else move.product_uom_qty * rng.uniform(0.3, 0.9)
                    move.write({'quantity': qty, 'picked': True})
                try:
                    picking.button_validate()
                except Exception as e:  # noqa: BLE001
                    self._log(f'  Aviso: entrega {so.name} no se pudo validar: {e}')

            if roll < 0.90:
                try:
                    invoice = so._create_invoices()
                    if journal:
                        invoice.journal_id = journal.id
                    if doc_type:
                        invoice.l10n_latam_document_type_id = doc_type.id
                    invoice.invoice_date = so.date_order
                    invoice.action_post()
                    n_facturas += 1
                    if n_dian < self.dian_sample_size:
                        self._try_dian_demo(invoice)
                        n_dian += 1
                except Exception as e:  # noqa: BLE001
                    self._log(f'  Aviso: factura de {so.name} no se pudo contabilizar: {e}')
            self._checkpoint(i + 1, target_confirm, 'Pedidos confirmados')
        self.created_pedidos = target_confirm
        self.created_facturas_venta = n_facturas
        self.created_facturas_dian = n_dian
        self._safe_commit()

    def _try_dian_demo(self, invoice):
        """Genera XML/CUFE DEMO real para una muestra de facturas (nunca
        se envía a la DIAN real: ver ALLOW_REAL_DIAN en este archivo)."""
        assert ALLOW_REAL_DIAN is False
        if invoice.journal_id.l10n_co_dian_operation_mode != 'demo':
            return
        edi_format = self.env['account.edi.format'].search(
            [('code', '=', 'l10n_co_dian_self')], limit=1)
        if not edi_format:
            return
        try:
            edi_format._l10n_co_post_invoices(invoice)
        except Exception as e:  # noqa: BLE001
            self._log(f'  Aviso: DIAN demo para {invoice.name} falló: {e}')

    # ------------------------------------------------------------------
    # 7. Notas crédito (siempre atadas a una factura real, nunca huérfanas)
    # ------------------------------------------------------------------

    def _generate_credit_notes(self, rng):
        self._log(f'Generando hasta {self.n_notas_credito} notas crédito...')
        posted_invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
            ('company_id', '=', self.env.company.id),
        ])
        if not posted_invoices:
            self.created_notas_credito = 0
            return
        # Tipo de documento LATAM "Nota Crédito Electrónica" (código 91):
        # sin asignarlo explícitamente queda vacío y el módulo DIAN OCA
        # falla al calcular el prefijo de numeración (bug real que
        # encontramos al probar esto por primera vez).
        nc_doc_type = self.env['l10n_latam.document.type'].search([
            ('code', '=', '91'), ('country_id.code', '=', 'CO'),
        ], limit=1)
        n = min(self.n_notas_credito, len(posted_invoices))
        sample = rng.sample(list(posted_invoices.ids), n)
        created = 0
        for i, inv_id in enumerate(sample):
            invoice = self.env['account.move'].browse(inv_id)
            reason = rng.choice(CREDIT_NOTE_REASONS)
            try:
                wiz = self.env['account.move.reversal'].with_context(
                    active_model='account.move', active_ids=invoice.ids,
                ).create({'reason': f'[DEMO] {reason}', 'journal_id': invoice.journal_id.id})
                wiz.reverse_moves()
                credit_note = wiz.new_move_ids
                if nc_doc_type:
                    credit_note.l10n_latam_document_type_id = nc_doc_type.id
                if reason in ('Devolución parcial', 'Descuento posterior'):
                    factor = rng.uniform(0.2, 0.7)
                    for line in credit_note.invoice_line_ids:
                        line.quantity = line.quantity * factor
                credit_note.action_post()
                created += 1
            except Exception as e:  # noqa: BLE001
                self._log(f'  Aviso: nota crédito de {invoice.name} falló: {e}')
            self._checkpoint(i + 1, n, 'Notas crédito')
        self.created_notas_credito = created
        self._safe_commit()

    # ------------------------------------------------------------------
    # 8. Pagos (parciales y completos, para poblar cartera con variedad)
    # ------------------------------------------------------------------

    def _register_payment(self, move, full, rng):
        wiz = self.env['account.payment.register'].with_context(
            active_model='account.move', active_ids=move.ids,
        ).create({})
        if not full:
            wiz.amount = round(wiz.amount * rng.uniform(0.2, 0.8), 2)
        wiz.action_create_payments()

    def _generate_payments(self, rng):
        self._log('Registrando pagos de clientes y proveedores...')
        out_invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'), ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', self.env.company.id),
        ])
        in_invoices = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'), ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', self.env.company.id),
        ])

        n_out = min(self.n_pagos_recibidos, len(out_invoices))
        n_in = min(self.n_pagos_realizados, len(in_invoices))
        n_pagos = 0
        for i, inv_id in enumerate(rng.sample(list(out_invoices.ids), n_out) if n_out else []):
            full = rng.random() < float(100 - self.pct_venta_contado) / 100 + 0.3
            try:
                self._register_payment(self.env['account.move'].browse(inv_id), full, rng)
                n_pagos += 1
            except Exception as e:  # noqa: BLE001
                self._log(f'  Aviso: pago recibido falló: {e}')
            self._checkpoint(i + 1, n_out, 'Pagos recibidos')
        self._safe_commit()

        for i, inv_id in enumerate(rng.sample(list(in_invoices.ids), n_in) if n_in else []):
            full = rng.random() < float(100 - self.pct_compra_contado) / 100 + 0.3
            try:
                self._register_payment(self.env['account.move'].browse(inv_id), full, rng)
                n_pagos += 1
            except Exception as e:  # noqa: BLE001
                self._log(f'  Aviso: pago realizado falló: {e}')
            self._checkpoint(i + 1, n_in, 'Pagos realizados')
        self.created_pagos = n_pagos
        self._safe_commit()

    # ------------------------------------------------------------------
    # 9. Validaciones automáticas
    # ------------------------------------------------------------------

    def _run_validations(self):
        self._log('Ejecutando validaciones automáticas...')
        checks = []

        # Débitos = Créditos en todos los asientos generados (Odoo lo
        # garantiza al contabilizar; se verifica igual como red de seguridad).
        moves = self.env['account.move'].search([
            ('state', '=', 'posted'), ('company_id', '=', self.env.company.id),
        ])
        unbalanced = moves.filtered(
            lambda m: not float_is_zero(sum(m.line_ids.mapped('balance')), precision_digits=2))
        checks.append(('Débitos = Créditos en todos los asientos', not unbalanced,
                        f'{len(unbalanced)} asientos descuadrados' if unbalanced else 'OK'))

        # Pedido -> Entrega -> Factura: toda factura de venta generada
        # referencia un pedido con al menos una entrega.
        sale_invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'), ('invoice_origin', '!=', False),
            ('company_id', '=', self.env.company.id),
        ])
        broken_chain = 0
        for inv in sale_invoices:
            so = self.env['sale.order'].search([('name', '=', inv.invoice_origin)], limit=1)
            # Un pedido compuesto solo por productos tipo "Servicio" nunca
            # genera entrega (no aplica, no es un error): solo cuenta como
            # descuadre si tiene líneas de producto almacenable sin entrega.
            has_storable_line = any(
                line.product_id.type != 'service' for line in so.order_line)
            if so and has_storable_line and not so.picking_ids:
                broken_chain += 1
        checks.append(('Cadena Pedido -> Entrega -> Factura', broken_chain == 0,
                        f'{broken_chain} facturas sin entrega asociada' if broken_chain else 'OK'))

        # Orden -> Recepción -> Factura para compras.
        purchase_invoices = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'), ('invoice_origin', '!=', False),
            ('company_id', '=', self.env.company.id),
        ])
        broken_po_chain = 0
        for inv in purchase_invoices:
            po = self.env['purchase.order'].search([('name', '=', inv.invoice_origin)], limit=1)
            if po and not po.picking_ids:
                broken_po_chain += 1
        checks.append(('Cadena Orden -> Recepción -> Factura', broken_po_chain == 0,
                        f'{broken_po_chain} facturas sin recepción asociada'
                        if broken_po_chain else 'OK'))

        # Factura - Pagos = Saldo (amount_residual ya lo calcula Odoo).
        wrong_residual = moves.filtered(
            lambda m: m.is_invoice() and m.payment_state == 'paid'
            and not float_is_zero(m.amount_residual, precision_digits=2))
        checks.append(('Factura - Pagos = Saldo', not wrong_residual,
                        f'{len(wrong_residual)} facturas "pagadas" con saldo pendiente'
                        if wrong_residual else 'OK'))

        # Inventario: Entradas - Salidas = Existencia, por producto.
        demo_products = self.product_tmpl_ids.mapped('product_variant_ids')
        stock_mismatch = 0
        for product in demo_products:
            valued_moves = self.env['stock.move'].search([
                ('product_id', '=', product.id), ('state', '=', 'done'),
                '|', ('is_in', '=', True), ('is_out', '=', True),
            ])
            computed = sum(m.quantity if m.is_in else -m.quantity for m in valued_moves)
            # Solo ubicaciones internas (bodegas reales): sumar todas las
            # ubicaciones incluiría las virtuales (Clientes/Proveedores/
            # Ajuste), que existen para cuadrar el grafo completo de
            # movimientos, no para representar existencia física.
            actual = sum(self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id.usage', '=', 'internal'),
            ]).mapped('quantity'))
            if not float_is_zero(computed - actual, precision_digits=2):
                stock_mismatch += 1
        checks.append(('Kardex: Entradas - Salidas = Existencia', stock_mismatch == 0,
                        f'{stock_mismatch} productos con descuadre'
                        if stock_mismatch else 'OK'))

        lines = ['VALIDACIÓN ERP COLOMBIA (lote DEMO)', '']
        all_ok = True
        for label, ok, detail in checks:
            mark = '✓' if ok else '✗ ERROR'
            lines.append(f'{label:45} {mark}  ({detail})')
            all_ok = all_ok and ok
        self.validation_report = '\n'.join(lines)
        self.validation_ok = all_ok
        self._log('\n' + self.validation_report)
        if not all_ok:
            self._log('ATENCIÓN: una o más validaciones fallaron. Ver validation_report.')
