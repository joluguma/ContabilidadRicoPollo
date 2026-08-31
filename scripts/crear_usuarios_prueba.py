# Crea 4 usuarios de PRUEBA en producción para validar los perfiles de
# acceso (grupos nativos de Odoo, sin módulo custom — ver decisión en
# la conversación: solo existe 1 usuario real hoy, así que no se
# justifica un módulo de roles a medida).
#
# Son cuentas claramente marcadas como prueba (login @ricopollo.test,
# dominio reservado que nunca resuelve — RFC 2606), pensadas para que
# el dueño entre con cada una y vea qué puede/no puede hacer. Se
# recomienda borrarlas cuando termine la prueba
# (env['res.users'].browse([...]).unlink()).
#
# Perfiles:
#   1. Contabilidad completa -> account.group_account_manager
#   2. Facturación/Cajero    -> account.group_account_invoice (sin manager)
#   3. Solo lectura          -> account.group_account_readonly (sin invoice)
#   4. Portal cliente        -> base.group_portal, sobre un partner de
#      prueba dedicado (NO un cliente real) con una factura de ejemplo,
#      para no exponer ni tocar datos de un cliente real.
#
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/crear_usuarios_prueba.py
Users = env['res.users']
Partner = env['res.partner']

PASSWORD = 'PruebaRicoPollo2026!'

def crear_usuario(login, name, group_xmlids, partner_id=None):
    existente = Users.search([('login', '=', login)], limit=1)
    if existente:
        print(f'  Ya existe, se omite: {login}')
        return existente
    vals = {
        'login': login,
        'name': name,
        'password': PASSWORD,
        'group_ids': [(6, 0, [env.ref(x).id for x in group_xmlids])],
    }
    if partner_id:
        vals['partner_id'] = partner_id
    user = Users.with_context(no_reset_password=True).create(vals)
    print(f'  Creado: {login} / {PASSWORD}  (grupos: {group_xmlids})')
    return user

print('1) Contabilidad completa')
crear_usuario(
    'prueba.contador@ricopollo.test', 'PRUEBA - Contador (acceso completo)',
    ['account.group_account_manager'],
)

print('2) Facturación / Cajero')
crear_usuario(
    'prueba.facturacion@ricopollo.test', 'PRUEBA - Facturación/Cajero',
    ['account.group_account_invoice'],
)

print('3) Solo lectura')
crear_usuario(
    'prueba.lectura@ricopollo.test', 'PRUEBA - Solo Lectura',
    ['account.group_account_readonly'],
)

print('4) Portal cliente (sobre un partner de prueba dedicado, no un cliente real)')
partner_prueba = Partner.search([('email', '=', 'prueba.portal@ricopollo.test')], limit=1)
if not partner_prueba:
    partner_prueba = Partner.create({
        'name': 'PRUEBA - Cliente Portal',
        'email': 'prueba.portal@ricopollo.test',
        'customer_rank': 1,
    })
    print('  Partner de prueba creado:', partner_prueba.id)

# Factura de ejemplo para que el portal no se vea vacío.
producto = env['product.product'].search([('sale_ok', '=', True), ('default_code', '!=', False)], limit=1)
factura_existe = env['account.move'].search([('partner_id', '=', partner_prueba.id), ('move_type', '=', 'out_invoice')], limit=1)
if not factura_existe and producto:
    factura = env['account.move'].create({
        'move_type': 'out_invoice',
        'partner_id': partner_prueba.id,
        'invoice_line_ids': [(0, 0, {
            'product_id': producto.id,
            'quantity': 2,
            'price_unit': producto.list_price,
        })],
    })
    factura.action_post()
    print('  Factura de ejemplo creada:', factura.name)

crear_usuario(
    'prueba.portal@ricopollo.test', 'PRUEBA - Cliente Portal',
    ['base.group_portal'],
    partner_id=partner_prueba.id,
)

env.cr.commit()
print('\nListo. Contraseña para las 4 cuentas:', PASSWORD)
