# Port a Odoo 19.0 (ERP Colombia)

Este módulo es un fork directo de [`OCA/account-closing`](https://github.com/OCA/account-closing),
módulo `account_fiscal_year_closing`, tomado de la rama `18.0` porque al
momento de este port **no existía todavía una rama `19.0`** publicada por
OCA. Se conserva la licencia original AGPL-3 y la autoría de OCA.

## Objetivo
Motor genérico de cierre de año fiscal (asientos de cierre y apertura),
requisito legal en Colombia. Ver [erp_colombia_contabilidad](../erp_colombia_contabilidad/)
para la plantilla de cierre específica del PUC colombiano que se
construye sobre este motor.

## Cambios hechos para que funcione en Odoo 19.0
Solo dos, ambos por renombres de API del framework, sin tocar la lógica
de negocio del módulo:

1. `tests/test_account_fiscal_year_closing.py`: `res.users.groups_id`
   fue renombrado a `group_ids` en Odoo 19.
2. `tests/test_account_fiscal_year_closing.py`: la referencia a
   `base.res_partner_4` (dato de demo) se reemplazó por `self.partner_a`,
   el partner de pruebas estándar de `AccountTestInvoicingCommon`, porque
   esta base de datos se instaló sin datos de demo.

Además, `_sql_constraints` (forma antigua de declarar restricciones
únicas) se migró a `models.Constraint(...)` en 3 lugares
(`account_fiscalyear_closing.py` x2, `account_fiscalyear_closing_template.py`
x1) porque Odoo 19 emite un warning de deprecación con la forma antigua.

Ningún archivo de `views/`, `security/` ni `wizards/` requirió cambios:
el módulo ya estaba escrito en el estilo moderno (sin `<tree>`, sin
`attrs`/`states`) y todos los campos/métodos de `account`/`res.company`
que usa (`chart_template`, `fiscalyear_last_day`, `fiscalyear_last_month`,
`fiscalyear_lock_date`, `_reverse_moves`) siguen existiendo igual en
Odoo 19.

## Pruebas
Test de integración original de OCA (`test_account_closing`), ejecutado
con `--test-enable --test-tags account_fiscal_year_closing`: **pasa**.
Cubre: factura de proveedor y cliente con IVA, cierre calculado, asientos
de cierre/apertura generados y balanceados, contabilización.

## Pendiente
Cuando OCA publique una rama `19.0` oficial de `account-closing`, evaluar
migrar a esa versión oficial en vez de mantener este fork.
