# Importa el balance de prueba (corte julio 2026) de GRUPO RICO POLLO SAS
# como un asiento de apertura en la base real (odoo19). Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/import_balance_rico_pollo.py
#
# Requiere haber corrido antes scripts/parse_balance_csv.py (genera
# scripts/balance_parsed.json, ya validado: total débitos = total
# créditos = 5.692.847.801,92).
import json
import re

DATA_PATH = 'scripts/balance_parsed.json'
CUTOVER_DATE = '2026-07-31'

with open(DATA_PATH, encoding='utf-8') as f:
    rows = json.load(f)

company = env.company
print('Compañía:', company.name, company.vat)

import re as _re


def puc_code(dotted):
    return _re.sub(r'\.', '', dotted)


# ------------------------------------------------------------------
# 1. Construir el árbol jerárquico del PUC (por código aplanado, sin
#    puntos: "1105." es padre de "1105.05." porque "110505" empieza
#    por "1105", no porque el texto con puntos lo haga — ese fue un bug
#    ya corregido) y calcular, para cada cuenta, el "residual" = su
#    propio Saldo Final menos lo que ya explican sus hijas (sub-cuentas
#    + detalle de terceros).
#
#    Esto reemplaza un enfoque binario anterior ("hoja vs. padre") que
#    asumía que toda cuenta con hijas es un subtotal puro. Eso es falso
#    en este archivo: cuentas como "41. OPERACIONALES" reciben más de
#    5.000 millones de pesos en movimientos DIRECTOS que sus sub-cuentas
#    visibles no explican en absoluto — omitirlos habría dejado fuera
#    miles de millones de ingresos reales. El residual de cada nodo
#    captura exactamente esa parte no explicada, en cualquier nivel del
#    árbol (para un subtotal puro, el residual da ~0 y no genera línea).
# ------------------------------------------------------------------
account_rows = [r for r in rows if not r['es_partner'] and r['codigo']]
account_codes = [r['codigo'] for r in account_rows]
flat_codes = {code: puc_code(code) for code in account_codes}
sf_by_code = {r['codigo']: r['saldo_final'] for r in account_rows}
desc_by_code = {r['codigo']: r['descripcion'] for r in account_rows}


def find_immediate_parent(code):
    best = None
    for other in account_codes:
        if other == code:
            continue
        if flat_codes[code] != flat_codes[other] and flat_codes[code].startswith(flat_codes[other]):
            if best is None or len(flat_codes[other]) > len(flat_codes[best]):
                best = other
    return best


parent_of = {code: find_immediate_parent(code) for code in account_codes}
account_children = {code: [] for code in account_codes}
for code, parent in parent_of.items():
    if parent:
        account_children[parent].append(code)

# El código real de cuenta (PUC) de una fila de tercero es el de la
# fila de cuenta inmediatamente anterior (no otro tercero).
current_account_code = None
partner_children = {code: [] for code in account_codes}
for r in rows:
    if not r['es_partner'] and r['codigo']:
        current_account_code = r['codigo']
        r['_parent_account_code'] = None
    else:
        r['_parent_account_code'] = current_account_code
        if r['es_partner'] and current_account_code:
            partner_children[current_account_code].append(r['saldo_final'])

residual_by_code = {}
for code in account_codes:
    explained = (
        sum(sf_by_code[child] for child in account_children[code])
        + sum(partner_children[code])
    )
    residual_by_code[code] = sf_by_code[code] - explained

# Excepción confirmada con el usuario: "1105.05. CAJA GENERAL" y
# "1105.06. CAJA CONSIGNACION" reconstruyen a saldos individuales de
# miles de millones (matemáticamente consistentes con su padre, pero
# fuera de toda proporción realista para una caja física). Se usa el
# saldo neto del padre "1105. CAJA" (cifra creíble) en vez de las dos
# subcuentas; su residual ya es ~0 (los hijos lo explican por completo)
# así que se agrega como línea aparte con su saldo propio.
ANOMALOUS_LEAF_CODES = {'1105.05.', '1105.06.'}
PARENT_OVERRIDE_CODE = '1105.'

leaf_account_rows = [
    {'codigo': code, 'descripcion': desc_by_code[code], 'saldo_final': residual_by_code[code]}
    for code in account_codes
    if abs(residual_by_code[code]) > 0.01 and code not in ANOMALOUS_LEAF_CODES
]
leaf_account_rows.append({
    'codigo': PARENT_OVERRIDE_CODE,
    'descripcion': desc_by_code[PARENT_OVERRIDE_CODE],
    'saldo_final': sf_by_code[PARENT_OVERRIDE_CODE],
})
print(f"Excepción aplicada: se usa el saldo neto de '{PARENT_OVERRIDE_CODE}' "
      f"({sf_by_code[PARENT_OVERRIDE_CODE]:,.2f}) en vez de "
      f"{sorted(ANOMALOUS_LEAF_CODES)} (ver PRODUCTION_CHECKLIST.md).")
partner_rows = [r for r in rows if r['es_partner'] and abs(r['saldo_final']) > 0.01]

print(f'Líneas a nivel de cuenta (residual != 0, incl. subtotales con movimiento directo): {len(leaf_account_rows)}')
print(f'Líneas de detalle por tercero: {len(partner_rows)}')


def account_type_for(code10):
    c1 = code10[0]
    c2 = code10[:2]
    if c1 == '1':
        if c2 == '11':
            return 'asset_cash'
        if c2 == '13':
            return 'asset_receivable'
        if c2 == '14':
            return 'asset_current'
        if c2 == '15':
            return 'asset_fixed'
        return 'asset_current'
    if c1 == '2':
        if c2 == '22':
            return 'liability_payable'
        return 'liability_current'
    if c1 == '3':
        return 'equity'
    if c1 == '4':
        return 'income'
    if c1 == '5':
        return 'expense'
    if c1 in ('6', '7'):
        return 'expense_direct_cost'
    return 'asset_current'


Account = env['account.account']
account_cache = {a.code: a for a in Account.search([('company_ids', 'in', company.id)])}


def get_or_create_account(dotted_code, name):
    code = puc_code(dotted_code)
    if code in account_cache:
        return account_cache[code]
    acc = Account.create({
        'code': code,
        'name': name[:100],
        'account_type': account_type_for(code),
        'company_ids': [(6, 0, [company.id])],
        'reconcile': account_type_for(code) in ('asset_receivable', 'liability_payable'),
    })
    account_cache[code] = acc
    print(f'  + Cuenta creada: {code} {name}')
    return acc


def is_debit_normal(dotted_code):
    """Clases PUC 1 (Activo), 5 (Gastos), 6 y 7 (Costos) son de
    naturaleza débito: un saldo positivo se contabiliza al débito.
    Clases 2 (Pasivo), 3 (Patrimonio) y 4 (Ingresos) son de naturaleza
    crédito: un saldo positivo se contabiliza al crédito (justo lo
    contrario) — mismo criterio usado para validar el parseo."""
    return dotted_code[0] in ('1', '5', '6', '7')


def debit_credit_for(dotted_code, saldo_final):
    if is_debit_normal(dotted_code):
        return (saldo_final, 0.0) if saldo_final > 0 else (0.0, -saldo_final)
    return (0.0, saldo_final) if saldo_final > 0 else (-saldo_final, 0.0)


# ------------------------------------------------------------------
# 2. Buscar el tercero por NIT (ya importado) para las líneas con detalle.
# ------------------------------------------------------------------
def partner_for_row(row):
    m = re.match(r'\[(\d+)\]', row['codigo'])
    if not m:
        return False
    nit = m.group(1)
    p = env['res.partner'].search([('vat', '=like', f'{nit}%')], limit=1)
    return p


# ------------------------------------------------------------------
# 3. Construir las líneas del asiento de apertura.
# ------------------------------------------------------------------
journal = env['account.journal'].search(
    [('type', '=', 'general'), ('company_id', '=', company.id)], limit=1)
print('Diario de apertura:', journal.name)

line_vals = []
skipped_no_account_ref = []

for r in leaf_account_rows:
    acc = get_or_create_account(r['codigo'], r['descripcion'])
    debit, credit = debit_credit_for(r['codigo'], r['saldo_final'])
    line_vals.append((0, 0, {
        'account_id': acc.id,
        'name': f"Apertura {r['descripcion']}"[:100],
        'debit': debit,
        'credit': credit,
    }))

for r in partner_rows:
    parent_code = r.get('_parent_account_code')
    if not parent_code:
        skipped_no_account_ref.append(r)
        continue
    # nombre de la cuenta: se toma de la fila de cuenta padre ya vista
    parent_row = next(
        (a for a in account_rows if a['codigo'] == parent_code), None)
    acc = get_or_create_account(parent_code, parent_row['descripcion'] if parent_row else parent_code)
    partner = partner_for_row(r)
    debit, credit = debit_credit_for(parent_code, r['saldo_final'])
    line_vals.append((0, 0, {
        'account_id': acc.id,
        'partner_id': partner.id if partner else False,
        'name': f"Apertura {r['descripcion']}"[:100],
        'debit': debit,
        'credit': credit,
    }))

total_debit = sum(v[2]['debit'] for v in line_vals)
total_credit = sum(v[2]['credit'] for v in line_vals)
print(f'\nTotal líneas: {len(line_vals)}')
print(f'Total débito: {total_debit:,.2f} | Total crédito: {total_credit:,.2f}')
print(f'Descuadre: {total_debit - total_credit:,.4f}')
print(f'Filas de tercero sin cuenta padre detectada: {len(skipped_no_account_ref)}')

# ------------------------------------------------------------------
# 4. Cuenta puente para cuadrar el asiento (redondeos de centavos por
#    la reconstrucción de decimales) — no debería superar unos pocos
#    pesos si la validación previa fue correcta.
# ------------------------------------------------------------------
diff = round(total_debit - total_credit, 2)
if abs(diff) >= 0.01:
    rounding_account = get_or_create_account('9999.', 'Ajuste por redondeo migración')
    line_vals.append((0, 0, {
        'account_id': rounding_account.id,
        'name': 'Ajuste por redondeo en migración de balance',
        'debit': -diff if diff < 0 else 0,
        'credit': diff if diff > 0 else 0,
    }))
    print(f'Línea de ajuste por redondeo agregada: {diff:,.2f}')

move = env['account.move'].create({
    'move_type': 'entry',
    'journal_id': journal.id,
    'date': CUTOVER_DATE,
    'ref': 'Apertura migración - Balance de prueba corte julio 2026',
    'line_ids': line_vals,
})
print('\nAsiento creado (borrador):', move.name, '| id:', move.id)
move.action_post()
print('Asiento contabilizado. Estado:', move.state)

env.cr.commit()
print('\nListo. Total cuentas en el plan ahora:', Account.search_count([('company_ids', 'in', company.id)]))
