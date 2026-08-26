# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo import models


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'erp.colombia.audit.mixin']

    def _erp_colombia_log_states(self, old_states, note):
        for move in self:
            old_state = old_states.get(move.id)
            if old_state is not None and old_state != move.state:
                move.erp_colombia_log_state_change(
                    'state', old_state, move.state, note=note)

    def action_post(self):
        old_states = {move.id: move.state for move in self}
        result = super().action_post()
        self._erp_colombia_log_states(old_states, 'Contabilización')
        return result

    def button_draft(self):
        old_states = {move.id: move.state for move in self}
        result = super().button_draft()
        self._erp_colombia_log_states(old_states, 'Vuelta a borrador')
        return result

    def button_cancel(self):
        old_states = {move.id: move.state for move in self}
        result = super().button_cancel()
        self._erp_colombia_log_states(old_states, 'Anulación')
        return result
