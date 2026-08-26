# ERP COLOMBIA — PROJECT STATUS

Última auditoría: 2026-08-26 (post-reconstrucción). Ver
`ARCHITECTURE.md` para el detalle técnico y `PRODUCTION_CHECKLIST.md`
para lo pendiente de producción.

## Dashboard

```
Arquitectura       █████████░ 90%
Seguridad          ███████░░░ 70%
Inventario         █████████░ 90%
Compras            █████████░ 90%
Ventas             ████████░░ 80%   (POS instalado, sin configurar/probar)
Contabilidad       ███████▌░░ 75%   (falta plantilla de cierre PUC)
Facturación DIAN   ██████░░░░ 60%   (pipeline completo en DEMO; 0% en producción real)
Reportes           ██████░░░░ 60%   (Kardex probado; resto instalado sin probar)
Producción         ███▌░░░░░░ 35%   (local endurecido; falta servidor/HTTPS/DIAN real)
Datos DEMO         ██████████ 100%  (SMALL y STANDARD probados end-to-end, 5/5 validaciones)
```

## A. Estado actual
Odoo 19.0 Community (`github.com/odoo/odoo`), corriendo local en macOS,
Python 3.11 (venv), PostgreSQL 18, 108 módulos instalados en `odoo19`.
`custom_addons/` versionado en git, separado del core de Odoo y de las
referencias OCA (que se reobtienen con `scripts/fetch_oca.sh`).

**Nota:** el 2026-08-26 se perdió todo el proyecto en disco (venv, git,
odoo/, custom_addons/) por una eliminación del usuario; se reconstruyó
completo desde el contexto de la sesión, reinstalado y verificado (10
tests automatizados, 0 fallos) contra una base de prueba desechable
antes de tocar las bases reales. Ver nota en `ARCHITECTURE.md`.

## B. Arquitectura
Ver `ARCHITECTURE.md`.

## C. Módulos propios — qué hace cada uno
| Módulo | Qué hace | Probado |
|---|---|---|
| `erp_colombia_core` | Menú raíz app, grupos Administrador/Auditor, modelo+mixin de auditoría | Instalación + smoke test manual |
| `erp_colombia_terceros` | DV del NIT (módulo 11, calculado y validado), nombre comercial | 5 tests automatizados, pasan |
| `erp_colombia_empresa` | Expone DV/nombre comercial en la ficha de Compañía | Manual |
| `erp_colombia_contabilidad` | Conecta el mixin de auditoría a `account.move` (facturas, NC/ND, comprobantes) | 3 tests automatizados, pasan |
| `erp_colombia_seguridad` | Perfiles de seguridad (Contador, Ventas, Inventario, etc.) sobre grupos nativos | 4 asserts vía shell, pasan |
| `erp_colombia_reportes` | Kardex (asistente + export Excel) | Test funcional con compra+venta real, saldo correcto |
| `erp_colombia_demo_data` | Motor de datos DEMO reproducible (terceros→compras→ventas→NC→pagos→kardex→DIAN demo), instalado **solo en `odoo19_demo`**, nunca en la base real | SMALL y STANDARD probados end-to-end (5/5 validaciones) + 1 test automatizado |
| `account_fiscal_year_closing` | Port a 19.0 del motor de cierre de año fiscal de OCA | 1 test OCA original + prueba con PUC real |

## D. Qué estamos aprovechando de Odoo (sin tocar el core)
`sale`, `purchase`, `stock`, `stock_account`, `account`, `account_edi`,
`account_edi_ubl_cii`, `account_debit_note`, `point_of_sale`, `contacts`,
`l10n_co`, `l10n_co_pos`, `l10n_latam_base`, `l10n_latam_invoice_document`,
`certificate`. Motor contable, de inventario y de contactos: 100% nativo.

## E. Qué estamos aprovechando de OCA
`l10n_co_electronic_invoice` (CIIU, municipios DANE, UNSPSC, tipos doc),
`l10n_co_electronic_invoice_self` (UBL+CUFE/CUDE+XAdES+SOAP),
`l10n_co_withholding_advance` (autorretención), `account_financial_report`
+ `account_tax_balance` (libros/reportes), `date_range`, `report_xlsx`.
Todas ramas `19.0` excepto `account_fiscal_year_closing` (portado desde
`18.0`, sin rama `19.0` publicada aún por OCA).

## F. DIAN — qué está y qué falta
**Implementado y probado (modo DEMO, sin red real):** generación XML UBL
2.1, firma XAdES real, sobre SOAP, cálculo de CUFE/CUDE (SHA-384),
documento adjunto. **Falta (trámite real, no código):** inscripción como
facturador electrónico software propio, Software ID/PIN reales,
certificado de producción, resolución autorizada, superar el set de
pruebas DIAN.
**Hallazgo importante documentado:** en modo demo/habilitación, el
módulo OCA lee los campos de numeración con sufijo `_test`
(`l10n_co_electronic_document_prefix_test`, etc.), no los normales —
fácil de configurar mal (nos pasó a nosotros mismos).

## G. Contabilidad — qué está y qué falta
PUC (384+ cuentas), IVA/retenciones (249 impuestos), CxC/CxP, libros
(Diario/Mayor/Balance de comprobación/Cartera vencida/IVA vía OCA),
motor de cierre de año fiscal (probado contra el PUC real). **Falta:**
la plantilla de cierre específica de Colombia — **DECISIÓN CONTABLE
PENDIENTE**, no se debe inventar.

## H. Inventario — qué está y qué falta
Motor completo (`stock`), valoración automática (costo promedio
ponderado), Kardex propio probado con compra+venta real y a escala
STANDARD (1.000 productos). Sin brechas conocidas.

## I. Seguridad — qué está y qué falta
Hecho: `admin_passwd`/`db_password` fuertes, servidor solo en
`127.0.0.1`, 9 grupos ERP Colombia (Administrador, Auditor, Contador,
Auxiliar contable, Facturación, Inventario, Compras, Ventas, Consulta).
**Falta:** `list_db=False` en producción, HTTPS/proxy.

## J. Producción — qué falta
Ver `PRODUCTION_CHECKLIST.md` completo.

## K. Deuda técnica
1. Documento Soporte y autorretención: instalados, sin caso de prueba
   propio dirigido (solo lectura de código + tests genéricos de OCA).
2. POS colombiano (`l10n_co_pos`) instalado, nunca configurado ni
   probado con una venta real.
3. El perfil "Consulta" solo cubre lectura contable (Odoo no tiene
   grupo nativo de solo lectura para ventas/compras/inventario).
4. **Ningún respaldo de archivos fuera del disco local** — causó la
   pérdida total del 2026-08-26. `git push` a un remoto real sigue
   pendiente (ver Roadmap).

## L. Riesgos
- Los módulos OCA de Colombia son recientes — auditar antes de
  producción real, especialmente autorretención (tarifa plana, no por
  concepto/tabla).
- `account_fiscal_year_closing` es un fork nuestro sin mantenimiento
  upstream garantizado.
- Sin respaldo remoto del código: un segundo incidente de disco
  perdería el trabajo de nuevo. Máxima prioridad del roadmap.

## M. Roadmap sugerido
1. **Máxima prioridad — Estabilidad/Continuidad**: crear un repositorio
   remoto real (GitHub privado u otro) y `git push`, para que un
   incidente de disco local no vuelva a borrar el proyecto entero.
2. **Contabilidad** — sesión con el contador para la plantilla de
   cierre PUC real.
3. **Validación** — Documento Soporte, autorretención, POS con casos
   reales.
4. **Producción** — servidor real, HTTPS, backups automatizados fuera
   de este Mac, trámite DIAN.
