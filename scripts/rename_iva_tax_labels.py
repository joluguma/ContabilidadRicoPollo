# Simplifica la etiqueta visible de los impuestos en órdenes de
# compra/venta y facturas: en vez de "19% IVA" / "0% IVA Exc" /
# "0% IVA E..." (nombre técnico + tarifa), se muestra solo la palabra
# IVA / Exento / Excluido. Es un cambio de solo etiqueta (campo name),
# no toca la tarifa (amount) ni el cálculo de impuestos.
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/rename_iva_tax_labels.py
RENAMES = {
    55: 'IVA',       # venta 19%
    56: 'IVA',       # venta 5%
    58: 'Exento',    # venta exento
    59: 'Excluido',  # venta excluido
    5: 'IVA',        # compra 19%
    6: 'IVA',        # compra 5%
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
