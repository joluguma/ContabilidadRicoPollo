"""Parser robusto para BALANCE DE PRUBEA CORTE JULIO.CSV.

El archivo fuente usa coma como separador decimal (convención colombiana)
pero también usa coma como separador de columnas CSV, así que cada cifra
con decimales quedó partida en 2 columnas físicas (ej. "52895700,7273002"
en vez de "52895700.7273002"). Como el número de columnas con decimales
varía fila a fila, se reconstruye probando todas las particiones posibles
de los tokens numéricos en 4 grupos (Saldo Anterior, Débitos, Créditos,
Saldo Final) y se valida cada una contra la identidad contable
Saldo Final = Saldo Anterior + Débitos - Créditos (tolerancia 1 centavo).
Las filas que no logran ninguna partición válida se reportan aparte para
revisión manual, nunca se adivinan.

Cuando una fila tiene MÁS DE UNA partición válida, elegir por magnitud
(ni "la más chica" ni "la más grande") es insuficiente: para una fila
"padre" con sub-cuentas, la reconstrucción correcta suele ser la de
MAYOR magnitud (coincide con la suma de sus hijas); para una línea de
detalle de tercero sin hijas, suele ser la de MENOR magnitud (evita
tomar un token largo como si fuera la parte entera de un monto). Por
eso este archivo NO decide el desempate — solo expone TODAS las
candidatas válidas por fila. El desempate jerárquico lo hace
`resolve_balance.py`, que sí conoce el árbol de cuentas.

Uso: python3 scripts/parse_balance_csv.py
"""
import csv
import itertools
import json

PATH = 'BALANCE DE PRUBEA CORTE JULIO.CSV'
TOLERANCE = 0.02


def try_partitions(tokens):
    """tokens: lista de fragmentos numéricos (str) que deben reconstruir
    4 números. Devuelve la lista de particiones válidas (cada una una
    tupla saldo_ant, debitos, creditos, saldo_final), sin elegir entre
    ellas — puede haber más de una que cuadre con la identidad contable
    por coincidencia aritmética."""
    n_extra = len(tokens) - 4
    if n_extra < 0 or n_extra > 4:
        return []
    candidates = []
    for decimal_slots in itertools.combinations(range(4), n_extra):
        sizes = [2 if i in decimal_slots else 1 for i in range(4)]
        if sum(sizes) != len(tokens):
            continue
        pos = 0
        nums = []
        ok = True
        for size in sizes:
            chunk = tokens[pos:pos + size]
            pos += size
            try:
                nums.append(float('.'.join(chunk)) if size == 2 else float(chunk[0]))
            except ValueError:
                ok = False
                break
        if not ok or len(nums) != 4:
            continue
        saldo_ant, debitos, creditos, saldo_final = nums
        # Cuentas de naturaleza débito (Activo/Gasto/Costo, PUC clase 1,5,6,7):
        #   Saldo Final = Saldo Anterior + Débitos - Créditos
        # Cuentas de naturaleza crédito (Pasivo/Patrimonio/Ingreso, clase 2,3,4):
        #   Saldo Final = Saldo Anterior - Débitos + Créditos
        # Se prueban ambas fórmulas y se acepta si alguna cuadra.
        if (abs((saldo_ant + debitos - creditos) - saldo_final) <= TOLERANCE
                or abs((saldo_ant - debitos + creditos) - saldo_final) <= TOLERANCE):
            candidates.append(nums)
    return candidates


def parse():
    with open(PATH, encoding='cp1252', newline='') as f:
        reader = list(csv.reader(f))

    rows = []
    unresolved = []
    for line_no, row in enumerate(reader, start=1):
        if len(row) < 3:
            continue  # línea vacía o de encabezado/metadata
        codigo, descripcion = row[0].strip(), row[1].strip()
        if not descripcion:
            continue
        tokens = [t.strip() for t in row[2:] if t.strip() != '']
        if not tokens:
            continue
        candidates = try_partitions(tokens)
        if not candidates:
            unresolved.append({
                'line': line_no, 'codigo': codigo, 'descripcion': descripcion,
                'tokens': tokens,
            })
            continue
        rows.append({
            'line': line_no,
            'codigo': codigo,
            'descripcion': descripcion,
            'es_partner': codigo.startswith('['),
            'candidatos': [
                [round(x, 6) for x in nums] for nums in candidates
            ],
        })
    return rows, unresolved


if __name__ == '__main__':
    rows, unresolved = parse()
    n_ambiguous = sum(1 for r in rows if len(r['candidatos']) > 1)
    print(f'Filas reconstruidas (>=1 partición válida): {len(rows)}')
    print(f'Filas sin partición válida (revisión manual): {len(unresolved)}')
    for u in unresolved[:30]:
        print(f"  línea {u['line']}: [{u['codigo']}] {u['descripcion']} -> {u['tokens']}")
    print(f'Filas con más de una partición posible (se resuelven en '
          f'resolve_balance.py con el árbol de cuentas): {n_ambiguous}')

    with open('scripts/balance_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    print("\nGuardado en scripts/balance_candidates.json "
          "(ejecutar ahora scripts/resolve_balance.py)")
