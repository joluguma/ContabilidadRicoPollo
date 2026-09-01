# Activa multi-bodega y crea las bodegas reales del negocio, con una
# ficha de contacto propia por bodega (dirección + observaciones en el
# campo "comment" del contacto — reutiliza res.partner, que ya tiene
# esos campos nativos, en vez de inventar un campo nuevo).
#
# "Centro de costo" (visto en la captura de referencia solo para
# BODEGA LA SEXTA) NO se implementa aquí: en Odoo eso corresponde a
# cuentas analíticas (account.analytic.account), que es una estructura
# contable aparte — se deja pendiente de una decisión explícita, no se
# improvisa.
#
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/crear_bodegas.py
company = env.company

# 1) Activar multi-ubicación (ajuste general, vía Settings) y el grupo
#    específico de "varias bodegas" (no expuesto como toggle en
#    Settings en esta versión) para el usuario actual — cuando se creen
#    cuentas reales de equipo, hay que darles este mismo grupo si van a
#    trabajar con más de una bodega.
config = env['res.config.settings'].create({'group_stock_multi_locations': True})
config.execute()
multi_wh_group = env.ref('stock.group_stock_multi_warehouses')
env.user.group_ids = [(4, multi_wh_group.id)]
print('Multi-ubicación y multi-bodega activados.')

# 2) Renombrar la bodega por defecto a "Principal" (coincide con la
#    fila "Principal" de la referencia, sin dirección ni observaciones).
principal = env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1, order='id')
if principal and principal.name != 'Principal':
    print(f'Bodega por defecto: "{principal.name}" -> "Principal"')
    principal.name = 'Principal'

# 3) Crear las bodegas reales.
BODEGAS = [
    {'name': 'BODEGA HIGUITA', 'code': 'HIGUI', 'obs': 'Centro de Acopio Materia prima primer y tercer piso'},
    {'name': 'BODEGA LA SEXTA', 'code': 'SEXTA', 'obs': 'Punto de Venta 1'},
    {'name': 'BODEGA PIEDRA SUR', 'code': 'PSUR', 'obs': 'FRACCIONAMIENTO DE ALIMENTOS'},
    {'name': 'VARIANTE NORTE', 'code': 'VNORT', 'obs': 'PLANTA PRODUCCIÓN LÍQUIDOS'},
]

Warehouse = env['stock.warehouse']
Partner = env['res.partner']

for b in BODEGAS:
    existente = Warehouse.search([('name', '=', b['name']), ('company_id', '=', company.id)], limit=1)
    if existente:
        print(f'  Ya existe, se omite: {b["name"]}')
        continue
    partner = Partner.create({
        'name': b['name'],
        'company_id': company.id,
        'comment': b['obs'],
        'type': 'other',
    })
    wh = Warehouse.create({
        'name': b['name'],
        'code': b['code'],
        'company_id': company.id,
        'partner_id': partner.id,
    })
    print(f'  Creada: {b["name"]} (código {b["code"]}, id {wh.id})')

env.cr.commit()
print('Listo.')
