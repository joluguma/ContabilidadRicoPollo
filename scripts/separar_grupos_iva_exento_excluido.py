# Separa "Exento" y "Excluido" en dos account.tax.group distintos.
#
# Hoy ambos comparten el mismo grupo "IVA 0%" (heredado de la
# configuración por defecto). Esto es un problema real: Exento y
# Excluido son categorías DIAN legalmente distintas (ver nota en
# res_partner/import scripts anteriores), y el resumen de impuestos
# nativo de Odoo (account.move.tax_totals, usado en la propia vista de
# factura Y en la tirilla) agrupa por tax_group_id — con el grupo
# compartido, la "Base Exenta" y la "Base Excluida" se mezclarían en
# una sola línea "IVA 0%", perdiendo justo la distinción que se pidió
# mostrar en la factura.
#
# Efecto: cambio de metadato (a qué grupo pertenece cada impuesto), no
# toca tarifas ni cálculos.
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/separar_grupos_iva_exento_excluido.py
TaxGroup = env['account.tax.group']
Tax = env['account.tax']

grupo_exento = TaxGroup.search([('name', '=', 'IVA Exento')], limit=1)
if not grupo_exento:
    grupo_exento = TaxGroup.create({'name': 'IVA Exento'})
    print('Creado grupo:', grupo_exento.name)

grupo_excluido = TaxGroup.search([('name', '=', 'IVA Excluido')], limit=1)
if not grupo_excluido:
    grupo_excluido = TaxGroup.create({'name': 'IVA Excluido'})
    print('Creado grupo:', grupo_excluido.name)

REASIGNAR = {
    58: grupo_exento,    # venta - Exento
    59: grupo_excluido,  # venta - Excluido
    10: grupo_exento,    # compra - Exento
    9: grupo_excluido,   # compra - Excluido
}

for tax_id, grupo in REASIGNAR.items():
    tax = Tax.browse(tax_id)
    print(f'{tax_id} ({tax.name}): grupo "{tax.tax_group_id.name}" -> "{grupo.name}"')
    tax.tax_group_id = grupo.id

env.cr.commit()
print('Listo.')
