# Dispara la generación de un lote STANDARD completo contra la base
# DEMO separada (nunca contra la base real). Puede tardar bastante
# (la corrida de referencia tomó ~65 minutos, sobre todo registrando
# pagos uno por uno). Pensado para correr en background:
#
#   python odoo-bin shell -c odoo_demo.conf --no-http \
#       < scripts/run_standard_batch.py > standard_batch_run.log 2>&1 &
batch = env['erp.colombia.demo.batch'].create({'mode': 'standard'})
batch._onchange_mode()
print(f"Iniciando lote STANDARD id={batch.id}: {batch.n_clientes} clientes, "
      f"{batch.n_proveedores} proveedores, {batch.n_productos} productos, "
      f"{batch.n_ordenes_compra} órdenes de compra, {batch.n_cotizaciones} "
      f"cotizaciones, {batch.n_pedidos} pedidos.")
batch.button_generate()
print("\n=== ESTADO FINAL:", batch.state, "===")
if batch.error_message:
    print("ERROR:", batch.error_message)
print("\n=== VALIDACIÓN ===")
print(batch.validation_report)
print("\n=== CONTEOS ===")
for f in ['created_clientes', 'created_proveedores', 'created_productos',
          'created_bodegas', 'created_cotizaciones', 'created_pedidos',
          'created_facturas_venta', 'created_facturas_dian',
          'created_notas_credito', 'created_ordenes_compra',
          'created_facturas_compra', 'created_pagos']:
    print(f, '=', batch[f])
print("\nBATCH_ID_RESULT=", batch.id)
