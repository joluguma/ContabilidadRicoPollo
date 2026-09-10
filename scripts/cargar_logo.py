# Carga el logo oficial de GRUPO RICO POLLO S.A.S. en la ficha de la
# compañía (res.company.logo). Odoo lo usa de forma nativa en:
#   - la página de inicio de sesión (/web/login)
#   - los encabezados de todos los PDF (facturas, órdenes de compra,
#     tirilla, cotizaciones, etc.)
# así que no hay que tocar código en cada módulo — basta con este campo.
#
# El logo se distribuye DENTRO del módulo del tema
# (piko_riko_theme/static/src/img/logo.png). El favicon se maneja con
# views/favicon_templates.xml.
#
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/cargar_logo.py
import base64

from odoo.tools import file_open

with file_open('piko_riko_theme/static/src/img/logo.png', 'rb') as f:
    raw = f.read()

company = env.company
company.logo = base64.b64encode(raw)
env.cr.commit()
print(f'Logo cargado en "{company.name}" ({len(raw)} bytes).')
print('Se refleja automáticamente en el login y en los PDF.')
