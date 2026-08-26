# ERP Colombia - Core

## Objetivo
Módulo núcleo del proyecto ERP Colombia. No contiene lógica de negocio de
inventario, contabilidad ni DIAN. Provee únicamente lo que los demás
módulos `erp_colombia_*` necesitan en común:

- Menú raíz de la aplicación "ERP Colombia" (`menu_erp_colombia_root`),
  al que los demás módulos deben anclar sus propios submenús.
- Grupos de seguridad base del proyecto: `group_erp_admin` (Administrador)
  y `group_erp_auditor` (Auditor).
- Mecanismo de auditoría transversal: modelo `erp.colombia.audit.log` y
  mixin `erp.colombia.audit.mixin`.

## Dependencias
- `base` (núcleo de Odoo, sin dependencias de otros módulos de negocio).

## Instalación
```
python odoo-bin -c odoo.conf -d <tu_base_de_datos> -i erp_colombia_core --stop-after-init
```

## Uso
Otros módulos `erp_colombia_*` que manejen documentos críticos deben
heredar el mixin y, para cambios de estado, llamar a
`erp_colombia_log_state_change`. El registro se consulta en
**ERP Colombia → Auditoría** (solo lectura).
