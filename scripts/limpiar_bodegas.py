# Dos arreglos sobre las bodegas reales:
#
# 1) Archiva una bodega "fantasma" vacía ("GRUPO RICO POLLO SAS -
#    warehouse # 6", código "varia") que apareció sin que nadie la
#    creara a propósito — 0 movimientos, 0 stock — y estaba
#    ensuciando el selector de "Ubicación de origen/destino" en los
#    traslados (aparecía como "varia" / "varia/Existencias").
#
# 2) Renombra las ubicaciones raíz de cada bodega real (hoy muestran
#    el CÓDIGO corto: "HIGUI", "SEXTA", "PSUR", "VNORT") al nombre
#    completo de la bodega, para que el selector de ubicaciones se
#    lea "BODEGA HIGUITA/Stock" en vez de "HIGUI/Stock" — el código
#    corto (HIGUI, SEXTA...) se sigue usando igual en los números de
#    traslado (ej. VNORT/INT/00001), eso no cambia.
#
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/limpiar_bodegas.py
Warehouse = env['stock.warehouse']

# 1) Bodega fantasma
fantasma = Warehouse.search([('code', '=', 'varia')])
for w in fantasma:
    print(f'Archivando bodega fantasma: "{w.name}" (código {w.code}, id {w.id})')
    w.view_location_id.action_archive()
    w.active = False

# 2) Renombrar ubicaciones raíz al nombre completo de la bodega
RENOMBRAR = {
    'HIGUI': 'BODEGA HIGUITA',
    'SEXTA': 'BODEGA LA SEXTA',
    'PSUR': 'BODEGA PIEDRA SUR',
    'VNORT': 'VARIANTE NORTE',
    'WH': 'Principal',
}
Location = env['stock.location']
for code, nombre in RENOMBRAR.items():
    loc = Location.search([('name', '=', code), ('usage', '=', 'view')], limit=1)
    if loc:
        print(f'Ubicación "{loc.name}" -> "{nombre}"')
        loc.name = nombre
    else:
        print(f'  No encontrada: {code}')

env.cr.commit()
print('Listo.')
