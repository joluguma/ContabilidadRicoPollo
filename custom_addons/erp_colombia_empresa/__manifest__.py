# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
{
    'name': 'ERP Colombia - Empresa',
    'version': '19.0.1.0.0',
    'category': 'ERP Colombia',
    'summary': 'Muestra el NIT+DV y el nombre comercial en la ficha de la compañía',
    'description': """
ERP Colombia - Empresa
========================

No agrega campos nuevos: `res.company` ya hereda de `res.partner` por
delegación (`_inherits`), así que el dígito de verificación y el nombre
comercial de `erp_colombia_terceros` ya existen en toda compañía. Este
módulo solo ajusta la vista de Compañía para mostrarlos junto a los
campos de configuración DIAN que ya trae la localización OCA
(`l10n_co_electronic_invoice`).
""",
    'author': 'ERP Colombia',
    'license': 'LGPL-3',
    'depends': ['erp_colombia_terceros', 'l10n_co_electronic_invoice'],
    'data': [
        'views/res_company_views.xml',
    ],
    'installable': True,
}
