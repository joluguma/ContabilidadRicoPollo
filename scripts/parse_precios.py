"""Parser para "LISTADO DE PRECIOS.xls" (GRUPO RICO POLLO SAS).

Mismo formato de reporte paginado que "LISTADO DE PRODUCTOS.xls" (ver
scripts/parse_productos.py) — se reutiliza la misma lógica de filtrado
de encabezados/pies de página repetidos y de exclusión de filas de
prueba.

Columnas de datos:
  0  CÓDIGO
  1  DESCRIPCIÓN
  3  PRECIO 1  (precio de venta principal — el que se usa por defecto)
  5  PRECIO 2  (precio alterno, muy poco usado — ~22 productos)
  8  PRECIO 3  (precio alterno, muy poco usado — ~45 productos)

No trae costo — el catálogo queda con costo en $0 hasta que se cargue
por otra vía.

Uso: python3 scripts/parse_precios.py
"""
import json

import xlrd

PATH = 'LISTADO DE PRECIOS.xls'

NON_PRODUCT_CODE0 = {
    'CÓDIGO',
    'Informe generado por Software System32 Enterprise',
    'SYSTEM32 - www.s3-la.com',
}

TEST_ROWS = {
    ('1000', 'EXENTO'), ('1001', 'EXCLUIDO'), ('1002', 'EXENTO 3'),
    ('1', 'PRUEBA'), ('1000', 'PRUEBA 5'), ('100100100', 'ARTICULO DE PRUEBA'),
}


def format_code(value):
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def parse():
    wb = xlrd.open_workbook(PATH)
    sheet = wb.sheet_by_index(0)

    prices = []
    for row_idx in range(sheet.nrows):
        code_raw = sheet.cell_value(row_idx, 0)
        description = sheet.cell_value(row_idx, 1)
        precio1 = sheet.cell_value(row_idx, 3)
        precio2 = sheet.cell_value(row_idx, 5)
        precio3 = sheet.cell_value(row_idx, 8)

        if isinstance(code_raw, str) and code_raw.strip() in NON_PRODUCT_CODE0:
            continue
        if code_raw in ('', None) or description in ('', None) or not isinstance(description, str):
            continue

        code = format_code(code_raw)
        description = description.strip()
        if (code, description) in TEST_ROWS:
            continue

        prices.append({
            'line': row_idx + 1,
            'codigo': code,
            'descripcion': description,
            'precio1': precio1 if isinstance(precio1, (int, float)) else 0.0,
            'precio2': precio2 if isinstance(precio2, (int, float)) else 0.0,
            'precio3': precio3 if isinstance(precio3, (int, float)) else 0.0,
        })
    return prices


if __name__ == '__main__':
    prices = parse()
    print(f'Precios extraídos: {len(prices)}')

    from collections import Counter
    code_counts = Counter(p['codigo'] for p in prices)
    dups = {c: n for c, n in code_counts.items() if n > 1}
    print(f'Códigos duplicados: {len(dups)}')
    for c, n in dups.items():
        print(f"  {c}: {[p['descripcion'] for p in prices if p['codigo'] == c]}")

    con_precio2 = [p for p in prices if p['precio2']]
    con_precio3 = [p for p in prices if p['precio3']]
    print(f'Con PRECIO 2 (!=0): {len(con_precio2)}')
    print(f'Con PRECIO 3 (!=0): {len(con_precio3)}')
    sin_precio1 = [p for p in prices if not p['precio1']]
    print(f'Sin PRECIO 1 (0 o vacío): {len(sin_precio1)}')

    with open('scripts/precios_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(prices, f, ensure_ascii=False, indent=1)
    print('\nGuardado en scripts/precios_parsed.json')
