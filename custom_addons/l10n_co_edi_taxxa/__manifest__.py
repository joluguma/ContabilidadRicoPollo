# Part of Piko Riko ERP. See LICENSE file for full copyright and licensing details.
{
    'name': 'Colombia - Facturación Electrónica TAXXA',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Conector con el proveedor tecnológico TAXXA para facturación electrónica DIAN',
    'description': """
Facturación Electrónica Colombia — TAXXA
=========================================

Conecta este ERP con TAXXA (https://taxxa.co), un proveedor tecnológico
autorizado por la DIAN, para emitir facturas electrónicas sin necesidad
de gestionar directamente la firma digital ni la habilitación técnica
ante la DIAN — eso lo hace TAXXA.

**Este módulo es una ALTERNATIVA al ya instalado
`l10n_co_electronic_invoice_self`** (conexión directa con la DIAN, sin
proveedor). Los dos caminos son excluyentes entre sí para un mismo
diario: se usa uno u otro, no ambos a la vez.

Estado actual (fase 1 de 2):
  * Configuración de credenciales TAXXA (Ajustes → Contabilidad, o en
    la ficha de la compañía).
  * Servicio de autenticación (solicitud de token) con botón
    "Probar conexión" para validar las credenciales contra el ambiente
    real de TAXXA.
  * Envío real de facturas/documentos POS y lectura de la respuesta
    (CUFE, QR, estado, XML/PDF) — pendiente hasta confirmar con TAXXA
    la estructura exacta de su respuesta (no documentada públicamente).
    Ver notas en models/taxxa_client.py.

No se inventa ningún dato de la API: cada campo implementado está
tomado directamente de la documentación técnica pública de TAXXA
(taxxa.info/menu-manual-tecnico), citada en el código.
""",
    'author': 'Piko Riko',
    'license': 'LGPL-3',
    'depends': ['account', 'l10n_co'],
    'data': [
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
}
