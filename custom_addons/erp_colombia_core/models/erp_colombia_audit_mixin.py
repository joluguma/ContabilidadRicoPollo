# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo import api, models


class ErpColombiaAuditMixin(models.AbstractModel):
    """Mixin de auditoría para modelos críticos de ERP Colombia.

    Los módulos erp_colombia_* que manejen documentos sensibles (facturas,
    notas crédito/débito, comprobantes contables, ajustes de inventario,
    configuración DIAN) deben heredar este mixin para registrar
    automáticamente creación/eliminación, y llamar a
    `erp_colombia_log_state_change` en las transiciones de estado que
    quieran dejar trazadas.
    """
    _name = 'erp.colombia.audit.mixin'
    _description = 'ERP Colombia - Mixin de auditoría'

    def erp_colombia_log_state_change(self, field_name, old_value, new_value, note=False):
        self.ensure_one()
        return self.env['erp.colombia.audit.log'].log(
            self, 'state_change', field_name=field_name,
            old_value=old_value, new_value=new_value, note=note,
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            self.env['erp.colombia.audit.log'].log(record, 'create')
        return records

    def unlink(self):
        for record in self:
            self.env['erp.colombia.audit.log'].log(record, 'unlink', note=record.display_name)
        return super().unlink()
