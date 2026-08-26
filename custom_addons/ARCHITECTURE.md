# ERP Colombia — Arquitectura

Ver `PROJECT_STATUS.md` para el estado (qué funciona, qué falta) y
`PRODUCTION_CHECKLIST.md` para lo pendiente de despliegue. Este
documento es sobre **cómo está organizado el código** y las
convenciones a seguir al seguir desarrollando.

## Capas

```
1. Core de Odoo (odoo/, addons/)
   No se toca. Se actualiza jalando el upstream oficial
   (github.com/odoo/odoo), nunca editando archivos ahí directamente.

2. Referencias OCA (custom_addons/oca_*)
   Clonadas con git, NO versionadas en nuestro repo (ver .gitignore).
   Se reobtienen con `scripts/fetch_oca.sh`. Se instalan tal cual,
   sin editarlas — si algo de OCA necesita un cambio, se hace por
   herencia desde un módulo erp_colombia_*, nunca editando el
   archivo de OCA en el sitio.
   Excepción: `custom_addons/account_fiscal_year_closing` SÍ es
   nuestro (fork explícito porque OCA no publicó rama 19.0 todavía —
   ver su PORT_NOTES.md). Ese sí se versiona y se edita.

3. Nuestro (custom_addons/erp_colombia_*)
   Todo por herencia (`_inherit`), nunca `_inherit` + redefinir
   `_name` de un modelo de Odoo salvo que sea un modelo genuinamente
   nuevo (ej. `erp.colombia.audit.log`, `erp.colombia.kardex.wizard`).
```

## Grafo de dependencias de nuestros módulos

```
erp_colombia_core            (sin dependencias de erp_colombia_*)
   ↑
   ├── erp_colombia_contabilidad   (+ account)
   ├── erp_colombia_seguridad      (+ account, sale, purchase, stock)
   │
erp_colombia_terceros          (+ contacts, l10n_co)
   ↑
   └── erp_colombia_empresa       (+ l10n_co_electronic_invoice)

erp_colombia_reportes          (+ stock_account, report_xlsx)
   — independiente, no depende de otros erp_colombia_*

erp_colombia_demo_data          (+ erp_colombia_core/terceros/empresa/
                                   contabilidad, sale_management,
                                   purchase, stock, account, l10n_co,
                                   l10n_co_electronic_invoice_self)
   — solo se instala en una base separada, nunca en la real

account_fiscal_year_closing    (+ account)
   — motor genérico, sin nada colombiano todavía;
     la plantilla PUC específica (pendiente, decisión contable)
     iría en erp_colombia_contabilidad, dependiendo de este módulo.
```

## Convención para un módulo nuevo `erp_colombia_x`

1. Antes de escribir código: ¿Odoo ya lo resuelve? ¿Un módulo OCA ya
   instalado lo resuelve? Documentar la respuesta en el README del
   módulo, aunque sea "no, por esto: ...".
2. Estructura mínima: `__init__.py`, `__manifest__.py`, `README.md`.
   Agregar `models/`, `views/`, `security/`, `wizards/`, `tests/` solo
   si hay contenido real — no crear carpetas vacías especulativas.
3. Herencia, no duplicación: `_inherit` sobre el modelo de Odoo que
   corresponda. Un modelo nuevo propio solo si el concepto no existe
   en Odoo (ej. el log de auditoría).
4. Todo módulo con lógica no trivial necesita al menos un test que
   falle si la lógica se rompe.
5. Todo hallazgo de compatibilidad con Odoo 19 (renombres de API,
   etc.) debe documentarse en el README o un `PORT_NOTES.md`.
6. Actualizar `PROJECT_STATUS.md` y `CHANGELOG.md` al terminar.

## Mecanismo de auditoría (`erp_colombia_core`)

Cualquier modelo que maneje documentos críticos debe heredar
`erp.colombia.audit.mixin`:

```python
class MiModelo(models.Model):
    _name = 'mi.modelo'
    _inherit = ['mi.modelo', 'erp.colombia.audit.mixin']
```

Esto da automáticamente auditoría de `create`/`unlink`. Para cambios de
estado explícitos, llamar:

```python
registro.erp_colombia_log_state_change('state', valor_anterior, valor_nuevo, note='...')
```

Ya conectado en: `account.move` (vía `erp_colombia_contabilidad`).

## Decisiones deliberadamente NO tomadas por el agente

Marcadas como **DECISIÓN CONTABLE PENDIENTE** en `PROJECT_STATUS.md`:

- Qué cuentas PUC cierran contra cuáles en el cierre de año fiscal.
- La tarifa y las cuentas de autorretención en producción real.
- Cuándo pasar los diarios de "demo"/"habilitación" a "producción" en
  la configuración DIAN (depende del trámite real ante la DIAN).

## Entorno de desarrollo (dos servidores)

- **`odoo.conf`** → base `odoo19`, puerto 8069: la compañía real.
- **`odoo_demo.conf`** → base `odoo19_demo`, puerto 8070: sandbox para
  `erp_colombia_demo_data`, completamente aislada (filestore propio en
  `.local_demo/`).

## Nota sobre el incidente del 2026-08-26

El proyecto completo (venv, git, odoo/, custom_addons/) fue eliminado
del disco por el usuario. Las bases de datos (`odoo19`, `odoo19_demo`)
no se vieron afectadas — Postgres las guarda fuera de esta carpeta. El
proyecto se reconstruyó desde el contenido que Claude tenía en el
contexto de la sesión (no había respaldo de archivos disponible);
verificado reinstalando en una base de prueba desechable y corriendo
los 10 tests automatizados (0 fallos). Lección: `git push` a un remoto
real (no solo commits locales) para no depender de que el disco local
sobreviva.
