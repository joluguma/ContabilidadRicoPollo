# Carga costo, impuesto (IVA/Exento/Excluido) y actualización de precio
# de venta desde "LISTADO PRECIOS 04 AGOSTO REVISAR.xlsx" (archivo más
# reciente y completo que el usado en import_precios_rico_pollo.py).
#
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/import_precios_completo.py
#
# Requiere haber corrido antes scripts/parse_precios_completo.py (genera
# scripts/precios_completo_parsed.json).
#
# Qué hace por producto (matching por default_code):
#   - taxes_id (impuesto de venta) y supplier_taxes_id (impuesto de
#     compra) -> se REEMPLAZAN por el impuesto correcto según el
#     archivo (IVA 19%/5%, Exento o Excluido). Antes estaban con el
#     default genérico de Odoo o vacíos.
#   - standard_price (costo) -> se carga por primera vez donde el
#     archivo trae COSTO (antes en $0 para todo el catálogo).
#   - list_price (precio de venta) -> se actualiza SOLO si el archivo
#     trae un PRECIO VENTA 1 distinto al ya cargado (24 casos de 966 —
#     este archivo es más nuevo/revisado que el anterior).
# No crea productos nuevos (todos los códigos de este archivo ya
# existen en el catálogo, cargados en la pasada anterior).
import json

DATA_PATH = 'scripts/precios_completo_parsed.json'

with open(DATA_PATH, encoding='utf-8') as f:
    rows = json.load(f)

print(f'Filas a procesar: {len(rows)}')

Product = env['product.template']
existing_by_code = {p.default_code: p for p in Product.search([('default_code', '!=', False)])}

no_encontrados = []
tax_actualizado = 0
costo_cargado = 0
precio_actualizado = []
sin_tax_key = []

for row in rows:
    code = row['codigo']
    product = existing_by_code.get(code)
    if not product:
        no_encontrados.append(code)
        continue

    if not row['tax_key']:
        sin_tax_key.append(code)
    else:
        vals = {}
        if row['sale_tax_id']:
            vals['taxes_id'] = [(6, 0, [row['sale_tax_id']])]
        if row['purchase_tax_id']:
            vals['supplier_taxes_id'] = [(6, 0, [row['purchase_tax_id']])]
        if vals:
            product.write(vals)
            tax_actualizado += 1

    if row['costo'] is not None and product.standard_price != row['costo']:
        product.standard_price = row['costo']
        costo_cargado += 1

    if row['precio1'] is not None and product.list_price != row['precio1']:
        precio_actualizado.append((code, product.list_price, row['precio1']))
        product.list_price = row['precio1']

env.cr.commit()

print(f'\nImpuestos actualizados: {tax_actualizado}')
print(f'Costos cargados/actualizados: {costo_cargado}')
print(f'Precios de venta actualizados: {len(precio_actualizado)}')
for c in precio_actualizado:
    print(' ', c)
print(f'\nCódigos del archivo no encontrados en el catálogo: {len(no_encontrados)}')
for c in no_encontrados:
    print(' ', c)
print(f'\nProductos sin impuesto reconocido (revisar manual): {len(sin_tax_key)}')
for c in sin_tax_key:
    print(' ', c)
