# Ejemplos reales de TAXXA — no inventados

Estos 3 archivos son copia LITERAL (carácter por carácter, incluyendo
inconsistencias de mayúsculas/minúsculas reales de TAXXA) de los
ejemplos que su propia documentación pública publica en:

- `invoice_con_propina.json` — https://taxxa.info/json-fe-con-propina/
- `credit_note_no_referenciada.json` — https://taxxa.info/json-nota-credito-no-referenciada/
- `debit_note.json` — https://taxxa.info/json-nota-debito-referenciada/
  (nota: el ejemplo publicado en esa URL en realidad no trae
  `jbillingreference`, salió igual de estructura que la nota sin
  referenciar — puede ser un error de su documentación, no nuestro).

**Por qué existen estos archivos**: el manual general de TAXXA
(`manual-general-json`) describe los campos en tablas, pero NO trae un
JSON completo funcional — solo estos ejemplos de páginas específicas sí
lo traen. Sirven de referencia de verdad (ground truth) para construir
el mapeo `account.move` → JSON TAXXA en la Fase 2, en vez de adivinar
la forma exacta de anidamiento/mayúsculas otra vez.

**Inconsistencias reales confirmadas entre estos ejemplos** (no son
error de copia, están así en su propia documentación):
- El parámetro de ambiente aparece como `"wEnvironment"` en el ejemplo
  de factura, pero como `"wenvironment"` (todo minúscula) en los
  ejemplos de notas. En pruebas en vivo contra el sandbox
  (`demo1.taxxa.co`), enviarlo con CUALQUIER grafía como parámetro de
  `fjDocumentAdd` fue rechazado (`rerror 797, "Parameter wenviroment is
  not valid for this method"`) — así que en la práctica NO se envía
  ese parámetro en absoluto; el ambiente lo determina la cuenta/URL.
- Nombres de campo mezclan mayúsculas inconsistentemente incluso
  dentro del mismo documento: `sStandardItemIdentification` (factura)
  vs `sstandarditemidentification` (notas), `jCajaPos` con J/C/P en
  mayúscula rodeado de campos todos en minúscula, etc. — al construir
  el mapeo, copiar la grafía exacta de este archivo para el tipo de
  documento correspondiente, no "corregirla" a algo más consistente.

**Confirmado en vivo, no en estos ejemplos**: enviando una factura con
esta misma estructura pero con el NIT real de Grupo Rico Pollo
(901909286) como vendedor, TAXXA respondió `rerror 3344, "The seller
document ... was not found in the DB."` — el vendedor debe estar dado
de alta en la plataforma de TAXXA antes de poder facturar. Probando
con el NIT de ejemplo de su propia documentación (901402281, que
tampoco está registrado bajo nuestra cuenta demo) se obtuvo
`rerror 9371, "Error actualizacion, Documento NO Generado, intente de
nuevo."` — un error genérico que no se pudo diagnosticar más sin
soporte de TAXXA o un NIT ya dado de alta en su plataforma (posible
causa: los códigos de departamento/ciudad DIAN (`wdepartmentcode`,
`wtowncode`) deben ser códigos exactos de su catálogo, no cualquier
número — pendiente de confirmar el catálogo real con TAXXA).
