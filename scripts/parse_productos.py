"""Parser para "LISTADO DE PRODUCTOS.xls" (GRUPO RICO POLLO SAS).

El archivo es un reporte paginado (formato .xls binario antiguo, 24
páginas) exportado por su sistema anterior (Software System32
Enterprise), no una tabla plana: cada página repite un bloque de
encabezado (datos de la compañía, "Fecha Reporte"/"Hora Reporte",
títulos de columna) y termina con un pie de página ("Informe generado
por...", "PÁGINA X DE Y", "SYSTEM32 - www.s3-la.com"). Hay que filtrar
esas filas repetidas para quedarse solo con los productos reales.

Columnas reales de datos (por índice, no coinciden con la posición del
texto del encabezado por cómo quedó formateado el reporte):
  0  CÓDIGO
  1  DESCRIPCIÓN
  3  DEPARTAMENTO (solo aparece en la primera fila de cada categoría;
     se "arrastra" hacia abajo hasta que cambia)
  11 CANTIDAD

El archivo NO trae precio ni costo — el catálogo se crea con precio en
$0, a completar después con otra fuente.

Se excluyen 6 filas de prueba del sistema anterior detectadas al inicio
del archivo (códigos "EXENTO", "EXCLUIDO", "PRUEBA", "ARTICULO DE
PRUEBA" — causaban códigos duplicados con productos reales).

Uso: python3 scripts/parse_productos.py
"""
import json

import xlrd

PATH = 'LISTADO DE PRODUCTOS.xls'

NON_PRODUCT_CODE0 = {
    'CÓDIGO',
    'Informe generado por Software System32 Enterprise',
    'SYSTEM32 - www.s3-la.com',
}

# (código, descripción) de las filas de prueba detectadas manualmente.
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

    products = []
    current_department = ''
    for row_idx in range(sheet.nrows):
        code_raw = sheet.cell_value(row_idx, 0)
        description = sheet.cell_value(row_idx, 1)
        department = sheet.cell_value(row_idx, 3)
        quantity = sheet.cell_value(row_idx, 11)

        if isinstance(code_raw, str) and code_raw.strip() in NON_PRODUCT_CODE0:
            continue
        if code_raw in ('', None) or description in ('', None) or not isinstance(description, str):
            continue

        code = format_code(code_raw)
        description = description.strip()
        if (code, description) in TEST_ROWS:
            continue

        if isinstance(department, str) and department.strip():
            current_department = department.strip().upper()

        products.append({
            'line': row_idx + 1,
            'codigo': code,
            'descripcion': description,
            'departamento': current_department,
            'cantidad': quantity if isinstance(quantity, (int, float)) else None,
        })
    return products


if __name__ == '__main__':
    products = parse()
    print(f'Productos extraídos: {len(products)}')

    from collections import Counter
    code_counts = Counter(p['codigo'] for p in products)
    dups = {c: n for c, n in code_counts.items() if n > 1}
    print(f'Códigos duplicados restantes: {len(dups)}')
    for c, n in dups.items():
        print(f"  {c}: {[p['descripcion'] for p in products if p['codigo'] == c]}")

    dept_counts = Counter(p['departamento'] for p in products)
    print('\nProductos por departamento:')
    for dept, n in dept_counts.most_common():
        print(f'  {dept or "(sin departamento)"}: {n}')

    with open('scripts/productos_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=1)
    print('\nGuardado en scripts/productos_parsed.json')
