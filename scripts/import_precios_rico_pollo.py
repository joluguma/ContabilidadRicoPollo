# Carga los precios de venta (PRECIO 1) al catálogo de GRUPO RICO POLLO
# SAS ya importado. Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/import_precios_rico_pollo.py
#
# Requiere haber corrido antes scripts/parse_precios.py (genera
# scripts/precios_parsed.json, ya validado: 972 precios, 0 duplicados).
#
# Decisión: solo se carga PRECIO 1 (precio de venta principal, el único
# con cobertura real — 972 de 972). PRECIO 2 y PRECIO 3 son precios
# alternos usados en muy pocos productos (20 y 19 respectivamente) y NO
# se cargan en esta pasada — quedan pendientes de una decisión sobre
# listas de precios múltiples si el negocio los necesita.
import json

DATA_PATH = 'scripts/precios_parsed.json'

with open(DATA_PATH, encoding='utf-8') as f:
    prices = json.load(f)

print(f'Precios a aplicar: {len(prices)}')

company = env.company
Product = env['product.template']
existing_by_code = {p.default_code: p for p in Product.search([('default_code', '!=', False)])}

Category = env['product.category']
salsamentaria = Category.search([('name', '=', 'SALSAMENTARIA')], limit=1)

updated, created, sin_cambio = 0, 0, []
for row in prices:
    code = row['codigo']
    price = row['precio1']
    product = existing_by_code.get(code)
    if product:
        if product.list_price != price:
            product.list_price = price
            updated += 1
        else:
            sin_cambio.append(code)
    else:
        new_product = Product.create({
            'name': row['descripcion'],
            'default_code': code,
            'categ_id': salsamentaria.id if salsamentaria else False,
            'type': 'consu',
            'is_storable': True,
            'sale_ok': True,
            'purchase_ok': True,
            'list_price': price,
        })
        existing_by_code[code] = new_product
        created += 1
        print(f'  + Producto creado (no estaba en el catálogo): {code} {row["descripcion"]} -> ${price:,.0f}')

env.cr.commit()
print(f'\nActualizados: {updated} | Creados: {created} | Sin cambio (ya tenían ese precio): {len(sin_cambio)}')

sin_precio = Product.search([('default_code', '!=', False), ('list_price', '=', 0)])
print(f'\nProductos que quedan en $0 (sin precio en el archivo): {len(sin_precio)}')
for p in sin_precio[:10]:
    print(f'  {p.default_code} {p.name}')
