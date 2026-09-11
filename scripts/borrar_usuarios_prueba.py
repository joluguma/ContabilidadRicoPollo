# Elimina las cuentas de PRUEBA (y su rastro) que se crearon para
# testear los perfiles de acceso. Ya cumplieron su función.
#
#   - 4 usuarios @ricopollo.test (contador, facturación, lectura, portal)
#   - el partner ficticio "PRUEBA - Cliente Portal"
#   - la factura de ejemplo INV/2026/00011 (se pasa a borrador y se
#     borra; queda un hueco en la numeración interna INV/2026 — no es
#     la secuencia electrónica DIAN, así que es aceptable)
#   - un borrador de factura de prueba que quedó sin confirmar
#
# Ejecutar con:
#   odoo-bin shell -c odoo.conf -d odoo19 --no-http < scripts/borrar_usuarios_prueba.py
Users = env['res.users']
users = Users.search([('login', 'like', '@ricopollo.test')])
print('Usuarios de prueba:', users.mapped('login'))

partner = env['res.partner'].search([('email', '=', 'prueba.portal@ricopollo.test')])

# 1) Facturas ligadas al partner ficticio o creadas por los usuarios prueba
Move = env['account.move']
moves = Move.search(['|',
                     ('partner_id', 'in', partner.ids),
                     ('create_uid', 'in', users.ids)])
for m in moves:
    print(f'  Factura {m.name or "(borrador)"} [{m.state}] -> se elimina')
    if m.state == 'posted':
        m.button_draft()
    if m.state != 'draft':
        m.button_cancel()
try:
    moves.unlink()
except Exception as e:
    print('  (no se pudo borrar alguna factura, se deja cancelada):', e)

# 2) Partner ficticio
if partner:
    try:
        partner.unlink()
        print('  Partner ficticio eliminado')
    except Exception as e:
        partner.active = False
        print('  Partner ficticio archivado (no se pudo borrar):', e)

# 3) Usuarios
for u in users:
    try:
        u.unlink()
        print(f'  Usuario {u.login} eliminado')
    except Exception as e:
        u.active = False
        print(f'  Usuario {u.login} archivado (no se pudo borrar): {e}')

# 4) Deshabilitar el registro público de cuentas ("¿No tienes una
#    cuenta?" en el login). Es un ERP interno: las cuentas se crean
#    desde Ajustes, no se registra nadie solo. La recuperación de
#    contraseña ("Restablecer contraseña") se deja activa.
env['ir.config_parameter'].sudo().set_param('auth_signup.invitation_scope', 'b2b')
print('Registro público de cuentas deshabilitado (solo por invitación).')

env.cr.commit()
print('Listo.')
