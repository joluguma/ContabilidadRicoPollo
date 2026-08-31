# Simplifica la etiqueta visible de los impuestos en órdenes de
# compra/venta y facturas: en vez de "19% IVA" / "0% IVA Exc" /
# "0% IVA E..." (nombre técnico traducido + tarifa/abreviatura), se
# muestra IVA/Exento/Excluido de forma clara. Es un cambio de solo
# etiqueta (campo name), no toca la tarifa (amount) ni el cálculo de
# impuestos.
#
# Nota: Odoo exige que el nombre del impuesto sea único, así que IVA
# 19% e IVA 5% no pueden llamarse ambos exactamente "IVA" — se
# mantiene la tarifa junto a la palabra (ej. "IVA 19%") para que sigan
# siendo distinguibles. Exento y Excluido sí quedan como una sola
# palabra porque cada uno es único en su tipo (venta/compra).
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/rename_iva_tax_labels.py
RENAMES = {
    55: 'IVA 19%',   # venta 19%
    56: 'IVA 5%',    # venta 5%
    58: 'Exento',    # venta exento
    59: 'Excluido',  # venta excluido
    5: 'IVA 19%',    # compra 19%
    6: 'IVA 5%',     # compra 5%
    10: 'Exento',    # compra exento
    9: 'Excluido',   # compra excluido
}

Tax = env['account.tax']
for tax_id, label in RENAMES.items():
    tax = Tax.browse(tax_id)
    old = tax.name
    tax.name = label
    print(f'{tax_id}: "{old}" -> "{label}"')

env.cr.commit()
print('Listo.')
