# ERP Colombia - Empresa

## Objetivo
Mostrar en la ficha de Compañía (Ajustes → Empresas) el nombre
comercial y el dígito de verificación del NIT que ya calcula
`erp_colombia_terceros`, junto a los campos DIAN que agrega la
localización OCA `l10n_co_electronic_invoice`. No define modelos ni
campos propios: `res.company` expone los campos de `res.partner`
mediante `related` (en Odoo 19, `res.company` ya no delega por
`_inherits` como en versiones anteriores).

## Dependencias
- `erp_colombia_terceros`
- `l10n_co_electronic_invoice` (OCA, precarga CIIU/regímenes/DIAN)

## Instalación
```
python odoo-bin -c odoo.conf -d <tu_base_de_datos> -i erp_colombia_empresa --stop-after-init
```

## Uso
Ajustes → Usuarios y Compañías → Compañías → (tu empresa): el nombre
comercial aparece junto a la razón social, y el DV junto al VAT.
