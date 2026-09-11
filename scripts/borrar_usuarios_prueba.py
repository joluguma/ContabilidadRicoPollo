# Retira las cuentas de PRUEBA que se crearon para testear los perfiles
# de acceso. Ya cumplieron su función.
#
#   - 4 usuarios @ricopollo.test -> se archivan (no pueden iniciar
#     sesión, no aparecen en las listas). Se archiva en vez de borrar
#     para evitar el cascade frágil de auth_signup/totp al hacer unlink.
#   - el partner ficticio "PRUEBA - Cliente Portal" -> se archiva
#   - la factura de ejemplo INV/2026/00011 -> se ANULA (queda con su
#     número, marcada como cancelada; no se borra para no dejar hueco
#     en la numeración). El borrador de factura de prueba sin confirmar
#     sí se borra.
#   - registro público de cuentas -> deshabilitado (solo por invitación)
#
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/borrar_usuarios_prueba.py
Users = env['res.users'].with_context(active_test=False)
users = Users.search([('login', 'like', '@ricopollo.test')])
print('Usuarios de prueba:', users.mapped('login'))

partner = env['res.partner'].with_context(active_test=False).search(
    [('email', '=', 'prueba.portal@ricopollo.test')])

# 1) Facturas
Move = env['account.move']
for m in Move.search([('partner_id', 'in', partner.ids)]):
    print(f'  Factura {m.name or "(borrador)"} [{m.state}] -> anular')
    if m.state == 'posted':
        m.button_draft()
        m.button_cancel()
for m in Move.search([('create_uid', 'in', users.ids), ('state', '=', 'draft')]):
    print(f'  Borrador de prueba {m.id} -> borrar')
    m.unlink()

# 2) Usuarios: archivar (sudo write directo, sin unlink)
for u in users:
    if u.active:
        u.sudo().write({'active': False})
        print(f'  Usuario {u.login} archivado')

# 3) Partner ficticio: archivar
if partner and partner.active:
    partner.sudo().write({'active': False})
    print('  Partner ficticio archivado')

# 4) Registro público de cuentas -> solo por invitación
env['ir.config_parameter'].sudo().set_param('auth_signup.invitation_scope', 'b2b')
print('Registro público de cuentas deshabilitado (solo por invitación).')

env.cr.commit()
print('Listo.')
