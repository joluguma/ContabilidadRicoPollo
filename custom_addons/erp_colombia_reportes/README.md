# ERP Colombia - Reportes

## Objetivo
Cubrir el único hueco de reportes detectado en la auditoría (Fase F) que
ni Odoo Community ni la localización OCA de Colombia resuelven: un
**Kardex** en el formato clásico usado en Colombia (fecha, documento,
tipo de movimiento, entrada, salida, saldo, costo unitario, costo total,
bodega). No reimplementa el motor de inventario/valorización: lee
directamente de `stock.move` (campos `value`, `is_in`, `is_out` que trae
`stock_account`).

## Dependencias
- `stock_account` (valorización automática de inventario)
- `report_xlsx` (OCA, para la exportación a Excel)

## Instalación
```
python odoo-bin -c odoo.conf -d <tu_base_de_datos> -i erp_colombia_reportes --stop-after-init
```
Requiere que la categoría de producto tenga valoración **Automática**
(Ajustes → Inventario → Valoración) — si no, no habrá `stock.move` con
`value` calculado y el Kardex saldrá vacío en costos.

## Uso
**ERP Colombia → Reportes → Kardex** (o **Inventario → Reporting →
Kardex**): elige producto, bodega (opcional, en blanco = todas) y rango
de fechas, pulsa **Generar**. Botón **Exportar a Excel** para descargar
el mismo detalle en `.xlsx`.
