# ERP Colombia — Changelog

Formato libre, orden cronológico descendente.

## 2026-08-26 (reconstrucción total)

### incident: pérdida total del proyecto en disco
El usuario eliminó intencionalmente todo el proyecto (`.git`, `venv/`,
`scripts/`, `odoo/`, `odoo-bin`, `custom_addons/*`, configs) salvo la
carpeta `addons/` oficial. Las bases de datos (`odoo19`, `odoo19_demo`)
no se vieron afectadas (Postgres las guarda aparte). No había respaldo
de archivos disponible (sin Time Machine configurado). Se reconstruyó
todo desde el contexto de la sesión: re-clon de Odoo 19.0 oficial,
venv nuevo, los 8 módulos propios recreados byte a byte según lo
escrito originalmente, y el port de `account_fiscal_year_closing`
re-clonado desde OCA 18.0 con los mismos 3 fixes de compatibilidad
reaplicados. Verificado: instalación limpia + 10 tests automatizados
(0 fallos) contra una base de prueba desechable antes de tocar
`odoo19`/`odoo19_demo` reales.

**Lección**: los commits locales no protegen contra la pérdida del
disco completo. Pendiente: `git push` a un remoto real.

## 2026-08-26 (motor de datos DEMO)

### feat: erp_colombia_demo_data
Motor de generación de datos DEMO reproducible (semilla), modos
SMALL/STANDARD/STRESS/CUSTOM. Genera terceros (NIT+DV+CIIU),
productos/categorías, bodegas, existencias variadas, ciclo completo de
compras y ventas, notas crédito, pagos, y una muestra de facturas con
DIAN demo real (XML/CUFE/firma XAdES, `ALLOW_REAL_DIAN=False` como
constante). 5 validaciones automáticas. Se instala en base separada
(`odoo19_demo`), nunca en la real.

Probado en SMALL y en STANDARD completo (1.000 clientes, 300
proveedores, 1.000 productos, 1.000 pedidos, 894 facturas, 1.429
pagos, ~65 min) — 5/5 validaciones.

Bugs reales encontrados y corregidos: el módulo OCA de DIAN lee los
campos de numeración `_test` en modo demo/habilitación (no los
normales); las notas crédito necesitan su tipo de documento LATAM
asignado a mano; Odoo bloquea commit/rollback en tests (resuelto con
`_safe_commit`/`_safe_rollback`); un pedido con más pedidos que
cotizaciones se resuelve generando más cotizaciones, no truncando; la
validación de cadena pedido→entrega excluye pedidos solo de servicios;
la limpieza granular choca con la inmutabilidad de movimientos de stock
"hechos" (documentado, no forzado con SQL crudo).

## 2026-08-26 (seguridad y auditoría)

### feat: erp_colombia_seguridad
7 perfiles (Contador, Auxiliar contable, Facturación, Inventario,
Compras, Ventas, Consulta) implicando grupos nativos de Odoo, sin
duplicar permisos. Administrador ERP Colombia ahora también otorga
`base.group_system`.

### feat: erp_colombia_contabilidad
Conecta el mixin de auditoría (creado en Fase D, sin usar hasta ahora)
a `account.move`: facturas, NC/ND y comprobantes quedan trazados.

## 2026-08-25/26 (base del proyecto)

### chore: instalación base
Odoo 19.0 Community + Python 3.11 (venv) + PostgreSQL 18 en local.
Compañía configurada como Colombia (país, moneda COP, PUC vía
`l10n_co`), idioma español instalado.

### feat: erp_colombia_core
Menú raíz, grupos Administrador/Auditor, modelo `erp.colombia.audit.log`
y mixin `erp.colombia.audit.mixin`.

### feat: erp_colombia_terceros
Cálculo y validación del DV del NIT (módulo 11), nombre comercial.

### feat: erp_colombia_empresa
Expone DV/nombre comercial en la ficha de Compañía.

### feat: l10n_co_electronic_invoice(_self) + account_financial_report
Instalados y probados los módulos OCA de facturación electrónica
colombiana (DIAN demo) y de reportes contables (Libro Mayor/Diario,
Balance de comprobación, Cartera vencida, IVA).

### feat: account_fiscal_year_closing — port a Odoo 19.0
Fork de `OCA/account-closing` 18.0. Renombres de API (`groups_id` →
`group_ids`, `_sql_constraints` → `models.Constraint`).

### feat: erp_colombia_reportes — Kardex
Único reporte que ni Odoo Community ni la localización OCA resuelven.
Probado con compra+venta real.

### security/chore
`admin_passwd`/`db_password` endurecidos, git inicializado (perdido y
reconstruido el 2026-08-26, ver arriba).
