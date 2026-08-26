mods = env['ir.module.module'].search([('state', '=', 'installed')])
mods._update_translations(['es_419'], True)
print("Traducciones actualizadas para", len(mods), "módulos")

dian = env['res.company'].search([('name', '=', 'dian')])
print("Empresa 'dian' encontrada:", dian.ids)
if dian:
    moves = env['account.move'].search_count([('company_id', 'in', dian.ids)])
    users = env['res.users'].search([('company_ids', 'in', dian.ids)])
    print("Movimientos contables en 'dian':", moves, "- Usuarios con acceso:", users.mapped('login'))

admin = env.ref('base.user_admin')
my_company = env.ref('base.main_company')
admin.write({'company_id': my_company.id})
if dian:
    admin.company_ids = [(3, dian.id)]  # quita el acceso, no borra la empresa todavía
    dian.write({'active': False})  # archiva en vez de borrar, reversible

env.cr.commit()
print("Compañía activa del admin ahora:", admin.company_id.name)
