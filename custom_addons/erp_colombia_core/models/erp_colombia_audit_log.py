# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ErpColombiaAuditLog(models.Model):
    _name = 'erp.colombia.audit.log'
    _description = 'ERP Colombia - Registro de auditoría'
    _order = 'date desc, id desc'
    _log_access = False

    user_id = fields.Many2one(
        'res.users', string='Usuario', required=True, readonly=True,
        default=lambda self: self.env.user)
    date = fields.Datetime(
        string='Fecha', required=True, readonly=True,
        default=fields.Datetime.now)
    model_name = fields.Char(string='Modelo', required=True, readonly=True)
    res_id = fields.Integer(string='ID Registro', required=True, readonly=True)
    document_ref = fields.Char(string='Documento', readonly=True)
    action = fields.Selection([
        ('create', 'Creación'),
        ('write', 'Modificación'),
        ('unlink', 'Eliminación'),
        ('state_change', 'Cambio de estado'),
    ], string='Acción', required=True, readonly=True)
    field_name = fields.Char(string='Campo', readonly=True)
    old_value = fields.Char(string='Valor anterior', readonly=True)
    new_value = fields.Char(string='Valor nuevo', readonly=True)
    note = fields.Char(string='Nota', readonly=True)

    @api.model
    def log(self, record, action, field_name=False, old_value=False, new_value=False, note=False):
        """Punto de entrada único para que los módulos erp_colombia_* registren auditoría.

        Se usa sudo() porque el usuario que ejecuta la acción auditada no
        necesariamente tiene permiso de escritura sobre el propio log.
        """
        return self.sudo().create({
            'user_id': self.env.user.id,
            'model_name': record._name,
            'res_id': record.id,
            'document_ref': record.display_name if record else False,
            'action': action,
            'field_name': field_name,
            'old_value': str(old_value) if old_value not in (False, None) else False,
            'new_value': str(new_value) if new_value not in (False, None) else False,
            'note': note,
        })
