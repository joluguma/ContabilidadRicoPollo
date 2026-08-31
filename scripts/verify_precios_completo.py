# Verifica, para TODOS los productos del archivo, que el impuesto que
# quedó en Odoo (taxes_id / supplier_taxes_id) coincide exactamente con
# lo que dice "LISTADO PRECIOS 04 AGOSTO REVISAR.xlsx" (tax_key ->
# sale_tax_id / purchase_tax_id ya resueltos en el JSON).
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/verify_precios_completo.py
import json

with open('scripts/precios_completo_parsed.json', encoding='utf-8') as f:
    rows = json.load(f)

Product = env['product.template']
existing_by_code = {p.default_code: p for p in Product.search([('default_code', '!=', False)])}

ok = 0
mismatches = []
no_encontrados = []

for row in rows:
    p = existing_by_code.get(row['codigo'])
    if not p:
        no_encontrados.append(row['codigo'])
        continue
    if not row['sale_tax_id']:
        continue
    sale_ids = p.taxes_id.ids
    purchase_ids = p.supplier_taxes_id.ids
    sale_ok = sale_ids == [row['sale_tax_id']]
    purchase_ok = purchase_ids == [row['purchase_tax_id']]
    if sale_ok and purchase_ok:
        ok += 1
    else:
        mismatches.append((row['codigo'], row['descripcion'], row['tax_key'], sale_ids, purchase_ids))

print(f'Coinciden exactamente con el archivo: {ok}')
print(f'No encontrados en catálogo: {len(no_encontrados)} -> {no_encontrados}')
print(f'Con diferencia: {len(mismatches)}')
for m in mismatches[:30]:
    print(' ', m)
