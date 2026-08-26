# ERP Colombia - Seguridad

## Objetivo
Perfiles de seguridad colombianos (Contador, Auxiliar contable,
Facturación, Inventario, Compras, Ventas, Consulta) para que asignar
acceso a un usuario sea elegir un perfil, no armar una combinación de
grupos nativos de Odoo cada vez. No se crea ningún permiso nuevo: cada
perfil solo implica (`implied_ids`) el grupo nativo de Odoo que ya
resuelve ese rol.

`Administrador` y `Auditor` ya existían en `erp_colombia_core` (Fase D);
este módulo además hace que `Administrador` (ERP Colombia) también
otorgue acceso técnico completo de Odoo (`base.group_system`), para que
sea un perfil verdaderamente único de "control total".

## Dependencias
- `erp_colombia_core`
- `account`, `sale`, `purchase`, `stock` (cada perfil implica un grupo
  nativo de uno de estos módulos)

## Instalación
```
python odoo-bin -c odoo.conf -d <tu_base_de_datos> -i erp_colombia_seguridad --stop-after-init
```

## Uso
Ajustes → Usuarios y Compañías → Usuarios → (usuario) → pestaña
"Permisos de acceso": los 7 perfiles aparecen bajo "ERP Colombia -
Perfiles". Marcar el que corresponda otorga automáticamente el grupo
nativo de Odoo asociado (ver tabla).

| Perfil | Grupo nativo que implica |
|---|---|
| Contador | `account.group_account_manager` (contabilidad completa + configuración) |
| Auxiliar contable | `account.group_account_user` (contabilidad completa, sin configuración) |
| Facturación | `account.group_account_invoice` (solo facturas y pagos) |
| Inventario | `stock.group_stock_manager` |
| Compras | `purchase.group_purchase_manager` |
| Ventas | `sales_team.group_sale_manager` |
| Consulta | `account.group_account_readonly` |

## Limitación conocida (no inventada, documentada a propósito)
Odoo no tiene un grupo nativo "solo lectura" para ventas, compras ni
inventario (solo para contabilidad). El perfil "Consulta" por ahora
solo cubre lectura contable.
