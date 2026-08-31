# Analiza "LISTADO PRECIOS 04 AGOSTO REVISAR.xlsx" y genera
# scripts/precios_completo_parsed.json con, por cada producto: costo
# (COSTO), precio de venta (PRECIO VENTA 1) e impuesto (IVA 19%/5%,
# EXENTO o EXCLUIDO), ya traducido a los tax_id reales de la base de
# producción (ver mapeo abajo).
#
# Excluye las 2 filas de plantilla/ejemplo (CODIGO "1").
#
# Mapeo de impuestos (confirmado por consulta directa a account.tax en
# producción, company_id=1):
#   Venta (taxes_id):            Compra (supplier_taxes_id):
#     IVA 19%      -> id 55        IVA 19%      -> id 5
#     IVA 5%       -> id 56        IVA 5%       -> id 6
#     EXENTO       -> id 58        EXENTO       -> id 10
#     EXCLUIDO     -> id 59        EXCLUIDO     -> id 9
#
# Caso especial detectado: código 1167 "COCO RAYADO SIMPLE" trae
# TIPO DE IMPUESTO="IVA" pero VALOR DE IMPUESTO=0 (inconsistente — un
# producto con IVA no puede tener tarifa 0, eso es Exento o Excluido).
# Se resuelve por VALOR DE IMPUESTO=0 -> EXCLUIDO (criterio: alimento
# básico sin procesar, la categoría 0% más común en este catálogo), y
# se deja marcado explícitamente en el reporte para que el cliente lo
# confirme con su contador si corresponde.
import json
import openpyxl

SRC = "LISTADO PRECIOS 04 AGOSTO REVISAR.xlsx"

TAX_SALE = {'IVA19': 55, 'IVA5': 56, 'EXENTO': 58, 'EXCLUIDO': 59}
TAX_PURCHASE = {'IVA19': 5, 'IVA5': 6, 'EXENTO': 10, 'EXCLUIDO': 9}

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb["Hoja1"]
rows = list(ws.iter_rows(min_row=3, values_only=True))

resultado = []
revisar_manual = []
sin_costo, sin_precio = [], []

for r in rows:
    codigo = r[0]
    if codigo is None:
        continue
    codigo = str(codigo).strip()
    if codigo == '1':
        continue  # fila de plantilla/ejemplo

    descripcion = r[1]
    costo = r[2]
    precio1 = r[4]
    tipo = r[21]
    valor = r[22]

    tipo_norm = (tipo or '').strip().upper()
    valor_norm = valor if isinstance(valor, (int, float)) else None

    tax_key = None
    if tipo_norm == 'IVA':
        if valor_norm == 19:
            tax_key = 'IVA19'
        elif valor_norm == 5:
            tax_key = 'IVA5'
        elif valor_norm == 0:
            tax_key = 'EXCLUIDO'
            revisar_manual.append((codigo, descripcion, tipo, valor, 'IVA con tarifa 0% -> asumido EXCLUIDO'))
        else:
            revisar_manual.append((codigo, descripcion, tipo, valor, 'IVA con tarifa no reconocida'))
    elif tipo_norm == 'EXENTO':
        tax_key = 'EXENTO'
    elif tipo_norm == 'EXCLUIDO':
        tax_key = 'EXCLUIDO'
    else:
        revisar_manual.append((codigo, descripcion, tipo, valor, 'TIPO DE IMPUESTO no reconocido'))

    if not costo:
        sin_costo.append(codigo)
    if not precio1:
        sin_precio.append(codigo)

    resultado.append({
        'codigo': codigo,
        'descripcion': descripcion,
        'costo': float(costo) if costo else None,
        'precio1': float(precio1) if precio1 else None,
        'tax_key': tax_key,
        'sale_tax_id': TAX_SALE.get(tax_key),
        'purchase_tax_id': TAX_PURCHASE.get(tax_key),
    })

with open('scripts/precios_completo_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print(f'Total productos procesados: {len(resultado)}')
print(f'Sin costo: {len(sin_costo)}')
print(f'Sin precio venta 1: {len(sin_precio)}')
print(f'\nCasos a revisar manualmente ({len(revisar_manual)}):')
for c in revisar_manual:
    print(' ', c)

from collections import Counter
print('\nDistribución de impuestos asignados:')
print(Counter(x['tax_key'] for x in resultado))
