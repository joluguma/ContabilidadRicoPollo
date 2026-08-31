# Renombra el usuario/partner de sistema "OdooBot" (autor de mensajes
# automáticos en el chatter, ej. "Transferir creado") a "Sistema", para
# que no aparezca la palabra "Odoo" en ningún lado de la interfaz.
# Cambio de solo nombre — no toca permisos, login ni funcionalidad.
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/renombrar_odoobot.py
NUEVO_NOMBRE = 'Sistema'

partner_root = env.ref('base.partner_root')
user_root = env.ref('base.user_root')

print(f'Partner: "{partner_root.name}" -> "{NUEVO_NOMBRE}"')
partner_root.name = NUEVO_NOMBRE

print(f'Usuario: "{user_root.name}" -> "{NUEVO_NOMBRE}"')
user_root.name = NUEVO_NOMBRE

env.cr.commit()
print('Listo.')
