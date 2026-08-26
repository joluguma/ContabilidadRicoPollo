# Ejecutar con: odoo-bin shell -c odoo.conf -d odoo19 < scripts/setup_co_company.py
lang = env['res.lang']._activate_lang('es_419')
print("Idioma es_419 activado:", lang)

company = env.ref('base.main_company')
co_country = env.ref('base.co')
cop_currency = env.ref('base.COP')

company.write({
    'country_id': co_country.id,
    'currency_id': cop_currency.id,
})
company.partner_id.write({'lang': 'es_419', 'country_id': co_country.id})

admin = env.ref('base.user_admin')
admin.write({'lang': 'es_419'})

env['account.chart.template'].try_loading('co', company, install_demo=False)

env.cr.commit()
print("Compañía configurada:", company.name, company.country_id.name, company.currency_id.name)
print("Plan de cuentas cargado:", env['account.account'].search_count([('company_ids', 'in', company.id)]))
