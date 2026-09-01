# Carga el conteo físico real (columna EXISTENCIA de "LISTADO PRECIOS
# 04 AGOSTO REVISAR.xlsx") como ajuste de inventario en la bodega
# Principal — usa el mecanismo nativo de Odoo (stock.quant en modo
# inventario + aplicar), el mismo que usa la pantalla "Inventario
# físico", para que quede el movimiento de stock real registrado.
#
# Requiere haber corrido antes scripts/parse_existencias.py.
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/import_existencias_principal.py
import json

DATA_PATH = 'scripts/existencias_parsed.json'

with open(DATA_PATH, encoding='utf-8') as f:
    rows = json.load(f)

print(f'Filas a procesar: {len(rows)}')

principal = env['stock.warehouse'].search([('name', '=', 'Principal')], limit=1)
if not principal:
    raise Exception('No se encontró la bodega "Principal"')
location = principal.lot_stock_id
print(f'Bodega destino: {principal.name} | ubicación: {location.display_name}')

Product = env['product.product']
existing_by_code = {p.default_code: p for p in Product.search([('default_code', '!=', False)])}

Quant = env['stock.quant'].with_context(inventory_mode=True)

actualizados = 0
sin_cambio = 0
no_encontrados = []

for row in rows:
    product = existing_by_code.get(row['codigo'])
    if not product:
        no_encontrados.append(row['codigo'])
        continue

    quant = Quant._gather(product, location, strict=True)
    if quant:
        quant = quant[0]
        if quant.quantity == row['existencia']:
            sin_cambio += 1
            continue
    else:
        quant = Quant.create({
            'product_id': product.id,
            'location_id': location.id,
            'inventory_quantity': 0,
        })

    quant.inventory_quantity = row['existencia']
    quant.action_apply_inventory()
    actualizados += 1

env.cr.commit()

print(f'\nActualizados: {actualizados}')
print(f'Sin cambio (ya tenían esa cantidad): {sin_cambio}')
print(f'Códigos no encontrados en el catálogo: {len(no_encontrados)}')
for c in no_encontrados[:20]:
    print('  ', c)
