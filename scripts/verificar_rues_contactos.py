# Audita los contactos colombianos con NIT cargado: vuelve a consultar
# RUES (con la validación de coincidencia EXACTA ya corregida) y
# compara el nombre que quedó guardado contra lo que RUES reporta hoy
# para ese mismo NIT.
#
# No corrige nada solo: reporta las diferencias para revisión manual,
# porque no se sabe si el dato guardado ya fue corregido a mano o si
# es el que quedó mal (por el bug de coincidencia por prefijo que ya
# se corrigió en el módulo, pero pudo haber afectado contactos creados
# ANTES de esa corrección).
#
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/verificar_rues_contactos.py
import time
import unicodedata


def normaliza(txt):
    txt = (txt or '').strip().upper()
    txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
    return txt


Partner = env['res.partner']
contactos = Partner.search([('vat', '!=', False), ('country_id.code', '=', 'CO')], order='is_company desc, id')
print(f'Contactos colombianos con NIT a revisar: {len(contactos)}')

sin_rues = 0
coinciden = 0
diferentes = []
errores = []

for i, p in enumerate(contactos):
    nit = (p.vat or '').split('-')[0].strip()
    if not nit.isdigit():
        continue

    # RUES limita las consultas por ráfaga (HTTP 429 "Too Many
    # Requests") — el primer intento de esta auditoría lo golpeó de
    # frente al consultar 470 contactos sin pausa (llegaron "429" en
    # milisegundos). Se espacia una consulta cada ~2s para no repetirlo.
    time.sleep(2)
    try:
        data = p._rues_fetch(nit)
    except Exception as e:
        errores.append((p.id, p.name, nit, str(e)))
        continue

    if not data:
        sin_rues += 1
        continue

    razon_social = data.get('razon_social') or ''
    if normaliza(razon_social) == normaliza(p.name):
        coinciden += 1
    else:
        diferentes.append({
            'id': p.id,
            'nit': nit,
            'nombre_actual': p.name,
            'nombre_rues': razon_social,
            'es_empresa': p.is_company,
        })

    if (i + 1) % 50 == 0:
        print(f'  ...{i + 1}/{len(contactos)} revisados')

print(f'\nSin registro en RUES para ese NIT (normal en personas naturales): {sin_rues}')
print(f'Coinciden con RUES: {coinciden}')
print(f'DIFERENTES de RUES (revisar): {len(diferentes)}')
for d in diferentes:
    print(f"  [{d['id']}] NIT {d['nit']} | Odoo: \"{d['nombre_actual']}\" | RUES: \"{d['nombre_rues']}\" | empresa={d['es_empresa']}")

if errores:
    print(f'\nErrores de consulta (no se pudo verificar): {len(errores)}')
    for e in errores[:10]:
        print(' ', e)

import json
with open('/tmp/rues_diferencias.json', 'w', encoding='utf-8') as f:
    json.dump(diferentes, f, ensure_ascii=False, indent=2)
print('\nGuardado detalle en /tmp/rues_diferencias.json')
