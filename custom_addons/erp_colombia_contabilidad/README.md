# ERP Colombia - Contabilidad

## Objetivo
Conectar el mixin de auditoría de `erp_colombia_core` a `account.move`:
facturas, notas crédito/débito y comprobantes contables manuales
quedan todos trazados, porque todos son `account.move` con distinto
`move_type`. No se crea ningún modelo ni motor contable nuevo.

## Dependencias
- `erp_colombia_core`
- `account`

## Instalación
```
python odoo-bin -c odoo.conf -d <tu_base_de_datos> -i erp_colombia_contabilidad --stop-after-init
```

## Uso
Cualquier `account.move` (factura, nota crédito/débito, asiento manual)
queda registrado en **ERP Colombia → Auditoría** al: crearse,
eliminarse, contabilizarse (`Contabilización`), volver a borrador
(`Vuelta a borrador`) o anularse (`Anulación`).

## Pendiente (decisión contable, no de código)
La plantilla de cierre de año fiscal del PUC colombiano no se define
aquí — es una decisión que debe tomar el contador de la empresa. El
motor que la ejecutará ya está instalado y probado
(`account_fiscal_year_closing`).

## Pruebas
`tests/test_account_move_audit.py` (3 tests): creación, contabilización
y anulación de una factura quedan registradas en el log de auditoría.
