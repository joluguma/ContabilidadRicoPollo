# ERP Colombia - Motor de Datos DEMO

## ⚠️ Antes que nada
**Este módulo nunca debe instalarse en la base de datos real de la
empresa.** Instálalo solo en una base separada dedicada a pruebas (ver
"Por qué una base separada" abajo). No existe ningún mecanismo en este
módulo que impida instalarlo en la base equivocada — es responsabilidad
de quien lo instala.

## Objetivo
Generar un escenario DEMO completo, coherente y reproducible (terceros,
productos, inventario, compras, ventas, notas crédito, pagos,
facturación electrónica DIAN en modo demo) para poder probar el ERP
completo sin usar información real. No crea ningún modelo de negocio
nuevo: reutiliza `sale`, `purchase`, `stock`, `account` y los módulos
`erp_colombia_*` tal cual.

## Por qué una base de datos separada
La compañía real con la que hemos trabajado en este proyecto (Odoo)
tiene NIT real, PUC configurado y datos reales. Generar miles de
clientes/facturas ahí la contaminaría permanentemente. Este módulo se
instala en una base nueva (ej. `odoo19_demo`) creada solo para esto:

```
createdb -U odoo -h localhost odoo19_demo
python odoo-bin -c odoo.conf -d odoo19_demo -i erp_colombia_demo_data --stop-after-init
```

Para "regenerar desde cero" de verdad, lo más simple y seguro es borrar
y recrear esa base (`dropdb` + `createdb` + reinstalar), no borrar
registro por registro. El asistente de limpieza en el menú (ver abajo)
es un complemento para resets parciales durante desarrollo iterativo,
no un sustituto de eso.

## Seguridad: `ALLOW_REAL_DIAN`
`ALLOW_REAL_DIAN = False` es una **constante de Python** en
`models/demo_batch.py`, no un campo de configuración — no existe forma
de cambiarla a `True` desde la interfaz, desde un wizard, ni desde un
parámetro. El código además lo verifica con un `assert` antes de tocar
cualquier diario configurado. Todas las facturas DEMO que pasan por
DIAN usan el diario en modo `demo` (firma con el certificado de
pruebas que trae el propio módulo OCA, respuesta simulada localmente,
**cero llamadas de red**).

## Reproducibilidad (`DEMO_SEED`)
Cada lote tiene un campo `seed` (entero). Con la misma semilla, `Faker`
y el generador de números aleatorios de Python producen exactamente la
misma secuencia de nombres/direcciones/cantidades.

## Modos
| Modo | Clientes | Proveedores | Productos | Pedidos | Compras |
|---|---|---|---|---|---|
| SMALL | 50 | 20 | 50 | 80 | 100 |
| STANDARD | 1.000 | 300 | 1.000 | 2.000 | 1.000 |
| STRESS | 10.000 | 5.000 | 10.000 | 50.000 | 20.000 |
| CUSTOM | (elige cada cantidad manualmente) | | | | |

## Interpretación de "empresas" vs "clientes"/"proveedores"
Decisión documentada: **"empresas" es el número de clientes que son
persona jurídica** (con NIT+DV+CIIU) dentro del total de clientes; el
resto son persona natural (cédula). Todos los proveedores se generan
como persona jurídica.

## Modo STANDARD — probado de verdad
Corrido completo (≈65 min, la mayor parte registrando pagos uno por
uno vía el wizard estándar de Odoo): 1.000 clientes, 300 proveedores,
1.000 productos, 20 bodegas, 1.000 cotizaciones, 1.000 pedidos
confirmados, 894 facturas de venta (20 con DIAN demo real), 300 notas
crédito, 1.000 órdenes de compra, 804 facturas de compra, 1.429 pagos.
**5/5 validaciones automáticas correctas.**

Dos ajustes que salieron de esa corrida a escala real (no aparecían
en SMALL):
- Si `n_pedidos` es mayor que `n_cotizaciones` (imposible en teoría —
  un pedido *es* una cotización confirmada), el generador crea
  automáticamente al menos tantas cotizaciones como pedidos se pidan.
- La validación "Pedido → Entrega → Factura" excluye pedidos
  compuestos **solo** por productos tipo "Servicio" (que legítimamente
  no generan entrega en Odoo).

## Uso
**ERP Colombia → Herramientas → Generador de datos DEMO** → crear un
registro nuevo, elegir modo, pulsar **Generar**. Corre las
validaciones automáticas al final y guarda el reporte en el propio
registro del lote.

## Validaciones automáticas incluidas
- Débitos = Créditos en todos los asientos generados.
- Cadena Pedido → Entrega → Factura íntegra.
- Cadena Orden de compra → Recepción → Factura íntegra.
- Factura "pagada" realmente tiene saldo (`amount_residual`) en cero.
- Kardex: entradas − salidas = existencia real, por producto.

## Limpieza
**ERP Colombia → Herramientas → Eliminar datos DEMO**: elige uno o más
lotes y confirma. Cada paso está aislado con un `SAVEPOINT`.

**Limitación real de Odoo, no un bug de este módulo**: los movimientos
de inventario en estado "hecho" son inmutables por diseño — un producto
con movimientos puede no poder eliminarse del todo. **Para un reset
garantizado al 100%, la vía real es borrar y recrear la base de datos
DEMO.**

## Pruebas
`tests/test_demo_generation.py`: lote diminuto (5 clientes, 3
proveedores, 6 productos), verifica estado `done`, conteos correctos,
validación pasa, y prefijo `[DEMO]` en todos los terceros.

Nota técnica: Odoo bloquea `commit()`/`rollback()` dentro de un test a
propósito; el motor detecta eso (`_safe_commit`/`_safe_rollback`) y no
hace nada en ese caso, sin perder los commits reales fuera de tests.
