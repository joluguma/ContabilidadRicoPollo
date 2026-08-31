# Pone en español (es_419) a todos los usuarios internos/portal que
# hayan quedado en inglés (los 4 usuarios de prueba se crearon antes de
# que el script de creación fijara el idioma por defecto).
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/fijar_idioma_espanol.py
Users = env['res.users']
en_espanol = Users.search([('lang', '!=', 'es_419')])
for u in en_espanol:
    print(f'{u.login}: {u.lang} -> es_419')
en_espanol.write({'lang': 'es_419'})
env.cr.commit()
print('Listo.')
