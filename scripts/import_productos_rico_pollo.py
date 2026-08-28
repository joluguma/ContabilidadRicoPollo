# Importa el catálogo de productos de GRUPO RICO POLLO SAS a la base
# real (odoo19). Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/import_productos_rico_pollo.py
#
# Requiere haber corrido antes scripts/parse_productos.py (genera
# scripts/productos_parsed.json, ya validado: 971 productos, 0 códigos
# duplicados, 3 departamentos).
#
# Decisión confirmada con el usuario: el archivo de origen no trae
# precio/costo, y su columna "Cantidad" tiene valores negativos poco
# confiables (posible artefacto del sistema anterior) — por eso este
# script SOLO crea el catálogo (código, nombre, categoría), sin tocar
# existencias. El inventario inicial real se carga después, aparte,
# con un conteo físico.
import json

DATA_PATH = 'scripts/productos_parsed.json'

with open(DATA_PATH, encoding='utf-8') as f:
    products = json.load(f)

print(f'Productos a importar: {len(products)}')

company = env.company
print('Compañía:', company.name)

Category = env['product.category']
category_cache = {c.name: c for c in Category.search([('name', 'in', list({p['departamento'] for p in products}))])}


def get_or_create_category(name):
    if name in category_cache:
        return category_cache[name]
    cat = Category.create({'name': name})
    category_cache[name] = cat
    print(f'  + Categoría creada: {name}')
    return cat


Product = env['product.template']
existing_by_code = {
    p.default_code: p for p in Product.search([('default_code', '!=', False)])
}

created, updated, skipped = 0, 0, []
for row in products:
    code = row['codigo']
    if code in existing_by_code:
        skipped.append(row)
        continue
    category = get_or_create_category(row['departamento'] or 'Sin categoría')
    Product.create({
        'name': row['descripcion'],
        'default_code': code,
        'categ_id': category.id,
        'type': 'consu',
        'is_storable': True,
        'sale_ok': True,
        'purchase_ok': True,
    })
    created += 1

env.cr.commit()
print(f'\nCreados: {created} | Ya existían (omitidos): {len(skipped)}')
print('Total productos en la base ahora:', Product.search_count([]))
