"""Resuelve las particiones ambiguas de scripts/balance_candidates.json
usando el árbol de cuentas PUC, en vez de una heurística de magnitud
ciega (que resultó insuficiente: para una fila "padre" con sub-cuentas
la reconstrucción correcta suele ser la de MAYOR magnitud —cuadra con
la suma de sus hijas—, pero para una línea de detalle de tercero sin
hijas suele ser la de MENOR magnitud —evita tomar un token largo como
si fuera la parte entera de un monto—).

Estrategia (bottom-up, hojas primero):
  - Filas SIN hijas (líneas de detalle de tercero, o cuentas hoja sin
    sub-cuentas ni terceros): se descartan candidatas cuyo Saldo Final
    exceda un techo de plausibilidad (3.000 millones — por encima de
    la mayor cifra legítima ya confirmada en este archivo a nivel de
    línea individual, 1.350 millones) y, entre las que quedan, se
    prefiere la de menor magnitud total.
  - Filas CON hijas (cuentas con sub-cuentas y/o detalle de terceros
    debajo): una vez resueltas las hijas, se elige la candidata cuyo
    Saldo Final quede más cerca de la suma de las hijas ya resueltas
    (lo normal es que el padre sea igual a esa suma; cuando no lo es
    —ej. "41. OPERACIONALES", que recibe ~5.000 millones en abonos
    directos que ninguna sub-cuenta explica— la candidata más cercana
    sigue siendo la correcta).

Uso: python3 scripts/resolve_balance.py
"""
import json
import re
from collections import defaultdict

LEAF_CEILING = 3_000_000_000  # ver docstring


def puc_code(dotted):
    return re.sub(r'\.', '', dotted)


def main():
    with open('scripts/balance_candidates.json', encoding='utf-8') as f:
        rows = json.load(f)

    account_rows = [r for r in rows if not r['es_partner'] and r['codigo']]
    account_codes = [r['codigo'] for r in account_rows]
    flat_codes = {c: puc_code(c) for c in account_codes}
    row_by_code = {r['codigo']: r for r in account_rows}

    def find_immediate_parent(code):
        best = None
        for other in account_codes:
            if other == code:
                continue
            if flat_codes[code] != flat_codes[other] and flat_codes[code].startswith(flat_codes[other]):
                if best is None or len(flat_codes[other]) > len(flat_codes[best]):
                    best = other
        return best

    parent_of = {c: find_immediate_parent(c) for c in account_codes}
    account_children = defaultdict(list)
    for c, p in parent_of.items():
        if p:
            account_children[p].append(c)

    # Adjuntar cada fila de tercero a la cuenta inmediatamente anterior.
    current = None
    partner_children = defaultdict(list)
    for r in rows:
        if not r['es_partner'] and r['codigo']:
            current = r['codigo']
        elif r['es_partner']:
            r['_parent_account_code'] = current
            if current:
                partner_children[current].append(r)

    resolved_sf = {}  # codigo -> saldo_final elegido (cuentas)
    resolved_full = {}  # codigo -> [sa, deb, cred, sf] elegido (cuentas)
    ambiguous_log = []

    def pick_leaf(row):
        cands = row['candidatos']
        if len(cands) == 1:
            return cands[0]
        plausible = [c for c in cands if abs(c[3]) <= LEAF_CEILING]
        pool = plausible if plausible else cands
        pool = sorted(pool, key=lambda c: sum(abs(x) for x in c))
        chosen = pool[0]
        ambiguous_log.append({
            'codigo': row['codigo'], 'descripcion': row['descripcion'],
            'tipo': 'hoja', 'n_candidatos': len(cands), 'elegida': chosen,
            'techo_aplicado': bool(plausible),
        })
        return chosen

    def pick_parent(row, children_sum):
        cands = row['candidatos']
        if len(cands) == 1:
            return cands[0]
        chosen = min(cands, key=lambda c: abs(c[3] - children_sum))
        ambiguous_log.append({
            'codigo': row['codigo'], 'descripcion': row['descripcion'],
            'tipo': 'padre', 'n_candidatos': len(cands), 'elegida': chosen,
            'suma_hijas': children_sum,
        })
        return chosen

    # Resolver primero todas las filas de tercero (siempre son hojas).
    for r in rows:
        if r['es_partner']:
            r['_resuelto'] = pick_leaf(r)

    def resolve_account(code):
        if code in resolved_sf:
            return resolved_sf[code]
        for child in account_children[code]:
            resolve_account(child)
        children_sum = (
            sum(resolved_sf[child] for child in account_children[code])
            + sum(pr['_resuelto'][3] for pr in partner_children[code])
        )
        row = row_by_code[code]
        has_children = bool(account_children[code]) or bool(partner_children[code])
        chosen = pick_parent(row, children_sum) if has_children else pick_leaf(row)
        resolved_full[code] = chosen
        resolved_sf[code] = chosen[3]
        return chosen[3]

    for code in account_codes:
        resolve_account(code)

    # Filas informativas sin código de cuenta (ej. "Total ACTIVO") no
    # participan de la jerarquía ni del asiento; se resuelven igual que
    # una hoja solo para poder mostrarlas/cruzarlas, con el mismo criterio
    # de plausibilidad.
    for r in rows:
        if not r['es_partner'] and not r['codigo']:
            r['_resuelto'] = pick_leaf(r)

    # Reconstruir el formato plano que espera import_balance_rico_pollo.py.
    out_rows = []
    for r in rows:
        if r['es_partner'] or not r['codigo']:
            sa, deb, cred, sf = r['_resuelto']
        else:
            sa, deb, cred, sf = resolved_full[r['codigo']]
        out_rows.append({
            'line': r['line'],
            'codigo': r['codigo'],
            'descripcion': r['descripcion'],
            'saldo_anterior': round(sa, 2),
            'debitos': round(deb, 2),
            'creditos': round(cred, 2),
            'saldo_final': round(sf, 2),
            'es_partner': r['es_partner'],
        })

    with open('scripts/balance_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(out_rows, f, ensure_ascii=False, indent=1)

    print(f'Filas resueltas: {len(out_rows)}')
    print(f'Filas ambiguas resueltas con criterio jerárquico: {len(ambiguous_log)}')
    biggest = sorted(ambiguous_log, key=lambda a: -abs(a['elegida'][3]))[:15]
    for a in biggest:
        print(f"  [{a['tipo']}] {a['codigo']:15} {a['descripcion'][:35]:35} "
              f"{a['n_candidatos']} candidatas -> SF={a['elegida'][3]:,.2f}")
    print("\nGuardado en scripts/balance_parsed.json — validar totales por "
          "clase con scripts/validate_balance.py antes de importar.")


if __name__ == '__main__':
    main()
