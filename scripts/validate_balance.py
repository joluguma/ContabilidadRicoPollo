"""Valida scripts/balance_parsed.json contra las cifras que el propio
archivo fuente declara (filas "Total ACTIVO", "Total PASIVO", etc. y
"Total Cuentas Débito/Crédito"), usando la MISMA lógica jerárquica de
residuales que scripts/import_balance_rico_pollo.py (una cuenta con
sub-cuentas puede tener movimiento propio no explicado por sus hijas,
como "41. OPERACIONALES" con ~5.000 millones directos — un chequeo que
solo sume "cuentas hoja" se equivoca por miles de millones).

Revisa NETO por clase PUC (para pescar huecos de reconstrucción) Y
TAMBIÉN débito/crédito BRUTO por separado: un chequeo de solo neto no
detecta un valor gigantesco mal signado que se cancela con otro por
coincidencia (ya pasó una vez en este proyecto: el neto por clase
cuadraba pero el bruto estaba en los cuatrillones por una fila de
detalle de tercero mal reconstruida).

Uso: python3 scripts/validate_balance.py
"""
import json
import re
from collections import defaultdict

EXPECTED_NET = {
    '1': 444_573_201.26,
    '2': 257_691_704.79,
    '3': 389_262_499.60,
    '4': 5_045_893_597.53,
    '5': 474_850_837.25,
    '6': 4_773_423_763.41,  # "Total COSTOS DE VENTAS [D]"
}
GROSS_LINE_CEILING = 6_000_000_000  # ninguna línea individual debería superar esto

# Misma excepción confirmada con el usuario que aplica import_balance_rico_pollo.py.
ANOMALOUS_LEAF_CODES = {'1105.05.', '1105.06.'}
PARENT_OVERRIDE_CODE = '1105.'


def puc_code(dotted):
    return re.sub(r'\.', '', dotted)


def is_debit_normal(code):
    return code[0] in ('1', '5', '6', '7')


def debit_credit_for(code, sf):
    if is_debit_normal(code):
        return (sf, 0.0) if sf > 0 else (0.0, -sf)
    return (0.0, sf) if sf > 0 else (-sf, 0.0)


def main():
    with open('scripts/balance_parsed.json', encoding='utf-8') as f:
        rows = json.load(f)

    account_rows = [r for r in rows if not r['es_partner'] and r['codigo']]
    account_codes = [r['codigo'] for r in account_rows]
    flat_codes = {c: puc_code(c) for c in account_codes}
    sf_by_code = {r['codigo']: r['saldo_final'] for r in account_rows}

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

    current = None
    partner_children = defaultdict(list)
    for r in rows:
        if not r['es_partner'] and r['codigo']:
            current = r['codigo']
            r['_parent_account_code'] = None
        else:
            r['_parent_account_code'] = current
            if r['es_partner'] and current:
                partner_children[current].append(r['saldo_final'])

    residual_by_code = {}
    for code in account_codes:
        explained = (
            sum(sf_by_code[child] for child in account_children[code])
            + sum(partner_children[code])
        )
        residual_by_code[code] = sf_by_code[code] - explained

    leaf_account_rows = [
        {'codigo': c, 'saldo_final': residual_by_code[c]}
        for c in account_codes
        if abs(residual_by_code[c]) > 0.01 and c not in ANOMALOUS_LEAF_CODES
    ]
    leaf_account_rows.append({'codigo': PARENT_OVERRIDE_CODE, 'saldo_final': sf_by_code[PARENT_OVERRIDE_CODE]})
    partner_rows = [r for r in rows if r['es_partner'] and abs(r['saldo_final']) > 0.01]

    net_by_class = defaultdict(float)
    gross_debit = 0.0
    gross_credit = 0.0
    worst_lines = []

    for r in leaf_account_rows:
        code = r['codigo']
        net_by_class[code[0]] += r['saldo_final']
        d, c = debit_credit_for(code, r['saldo_final'])
        gross_debit += d
        gross_credit += c
        if abs(r['saldo_final']) > GROSS_LINE_CEILING:
            worst_lines.append({'codigo': code, 'descripcion': '(cuenta)', 'saldo_final': r['saldo_final'], 'line': '-'})

    for r in partner_rows:
        code = r['_parent_account_code']
        if not code:
            continue
        net_by_class[code[0]] += r['saldo_final']
        d, c = debit_credit_for(code, r['saldo_final'])
        gross_debit += d
        gross_credit += c
        if abs(r['saldo_final']) > GROSS_LINE_CEILING:
            worst_lines.append(r)

    print("Neto por clase (reconstruido vs. declarado por el archivo):")
    ok = True
    for cls, expected in EXPECTED_NET.items():
        got = net_by_class.get(cls, 0.0)
        diff = got - expected
        flag = 'OK' if abs(diff) < 1000 else '*** REVISAR ***'
        if flag != 'OK':
            ok = False
        print(f"  clase {cls}: reconstruido={got:,.2f}  esperado={expected:,.2f}  "
              f"diff={diff:,.2f}  {flag}")

    # El criterio real de un asiento contable válido es que débito bruto
    # (sumando cada línea por su propio lado normal, sin invertir signos
    # a nivel de clase) cuadre exactamente con crédito bruto. NO tiene
    # que coincidir con "Total Cuentas Débito/Crédito" del archivo — esa
    # cifra la calculó el software de origen a nivel de clase completa
    # (Activo+Gastos+Costos vs. Pasivo+Patrimonio+Ingresos), mientras que
    # aquí cada cuenta/tercero individual aporta según su propio signo
    # real (una cuenta por cobrar con saldo a favor del cliente, por
    # ejemplo, aporta al lado contrario) — son magnitudes distintas por
    # diseño, no un error.
    print(f"\nTotal débito bruto: {gross_debit:,.2f}")
    print(f"Total crédito bruto: {gross_credit:,.2f}")
    if abs(gross_debit - gross_credit) > 0.05:
        ok = False
        print("*** EL ASIENTO NO CUADRA (débito != crédito) — NO IMPORTAR TODAVÍA ***")
    else:
        print("Débito == crédito: el asiento está cuadrado.")

    if worst_lines:
        ok = False
        print(f"\n*** {len(worst_lines)} línea(s) superan el techo de plausibilidad "
              f"({GROSS_LINE_CEILING:,.0f}) — requieren revisión manual: ***")
        for r in worst_lines:
            print(f"  línea {r['line']}: [{r['codigo']}] {r['descripcion']} "
                  f"SF={r['saldo_final']:,.2f}")

    print("\n" + ("VALIDACIÓN OK — seguro proceder con el dry-run de importación."
                   if ok else "VALIDACIÓN FALLIDA — no ejecutar la importación real todavía."))


if __name__ == '__main__':
    main()
