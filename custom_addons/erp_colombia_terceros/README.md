# ERP Colombia - Terceros

## Objetivo
Extender `res.partner` (contactos, incluye empresas vía `res.company`)
para cubrir dos huecos identificados en la auditoría: ni Odoo Community
ni la localización OCA (`l10n_co_electronic_invoice`) calculan o validan
el dígito de verificación del NIT, y no existe un campo de nombre
comercial separado de la razón social.

## Dependencias
- `contacts` (core de Odoo)
- `l10n_co` (para el tipo de identificación NIT, `l10n_co.rut`)

## Instalación
```
python odoo-bin -c odoo.conf -d <tu_base_de_datos> -i erp_colombia_terceros --stop-after-init
```

## Uso
- Escribe el NIT en el campo VAT sin el dígito (ej. `800197268`): el
  campo DV se completa automáticamente.
- Si prefieres escribir el DV a mano con guion (ej. `800197268-4`), el
  sistema valida que sea el correcto y rechaza el guardado si no lo es.
- El campo **Nombre comercial** aparece junto al nombre para contactos
  tipo empresa.

Algoritmo usado: módulo 11 con la serie de primos de la DIAN (Orden
Administrativa 04 de 1989): `3,7,13,17,19,23,29,37,41,43,47,53,59,67,71`
aplicados de derecha a izquierda sobre los dígitos del NIT.

## Pruebas
`tests/test_verification_digit.py` (5 tests): valores conocidos del
algoritmo, cómputo automático, contacto sin NIT no calcula DV, rechazo
de DV incorrecto, aceptación de DV correcto.
