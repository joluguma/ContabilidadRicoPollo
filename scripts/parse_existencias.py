# Extrae código + EXISTENCIA de "LISTADO PRECIOS 04 AGOSTO REVISAR.xlsx"
# para cargarlo como conteo físico real en la bodega Principal.
#
# Validado antes de usarlo (ver conversación): a diferencia de
# "LISTADO DE PRODUCTOS.xls" (que resultó ser una diferencia contra un
# conteo anterior, con 221 negativos — NO se usa), esta columna
# EXISTENCIA no tiene ningún valor negativo (0 de 966), lo que es
# consistente con ser un conteo físico real.
#
# Filas sin EXISTENCIA (en blanco) se EXCLUYEN — no se asume que
# "en blanco" signifique 0, para no afirmar un dato que no viene del
# conteo real.
import json
import openpyxl

SRC = "LISTADO PRECIOS 04 AGOSTO REVISAR.xlsx"

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb["Hoja1"]
rows = list(ws.iter_rows(min_row=3, values_only=True))

resultado = []
sin_valor = 0
for r in rows:
    codigo = r[0]
    if codigo is None:
        continue
    codigo = str(codigo).strip()
    if codigo == '1':
        continue  # fila de plantilla/ejemplo

    existencia = r[16]
    if existencia is None:
        sin_valor += 1
        continue
    try:
        existencia = float(existencia)
    except (TypeError, ValueError):
        sin_valor += 1
        continue

    resultado.append({'codigo': codigo, 'descripcion': r[1], 'existencia': existencia})

with open('scripts/existencias_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

negativos = [x for x in resultado if x['existencia'] < 0]
print(f'Productos con existencia real a cargar: {len(resultado)}')
print(f'Sin valor de existencia (se dejan como están): {sin_valor}')
print(f'Negativos (no debería haber ninguno): {len(negativos)}')
for n in negativos:
    print('  ', n)
