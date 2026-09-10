# Carga el logo oficial de GRUPO RICO POLLO S.A.S. en la ficha de la
# compañía (res.company.logo). Odoo usa ese campo de forma nativa en:
#   - la página de inicio de sesión (/web/login)
#   - los encabezados de todos los PDF (facturas, órdenes de compra,
#     tirilla, cotizaciones, etc.)
# así que no hay que tocar código en cada módulo — basta con este campo.
#
# El archivo debe estar en la raíz del proyecto como
# 'logo_grupo_rico_pollo.png' (o .jpg / .jpeg / .webp). Ideal: PNG con
# fondo transparente, pero funciona cualquier formato.
#
# (El favicon —ícono de la pestaña del navegador— se maneja aparte, con
# una plantilla en el tema, porque en Odoo 19 Community res.company ya
# no tiene el campo favicon.)
#
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/cargar_logo.py
import base64
import os

CANDIDATOS = [
    'logo_grupo_rico_pollo.png',
    'logo_grupo_rico_pollo.jpg',
    'logo_grupo_rico_pollo.jpeg',
    'logo_grupo_rico_pollo.webp',
]

ruta = next((c for c in CANDIDATOS if os.path.exists(c)), None)
if not ruta:
    raise Exception(
        "No se encontró el archivo del logo. Guardá el logo como "
        "'logo_grupo_rico_pollo.png' en la raíz del proyecto y volvé a correr."
    )

print(f'Usando: {ruta}')
with open(ruta, 'rb') as f:
    raw = f.read()

company = env.company
company.logo = base64.b64encode(raw)
env.cr.commit()
print(f'Logo cargado en la compañía "{company.name}" ({len(raw)} bytes).')
print('Se refleja automáticamente en el login y en los PDF.')
