# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountMoveAudit(AccountTestInvoicingCommon):

    def test_create_is_logged(self):
        log_model = self.env['erp.colombia.audit.log']
        before = log_model.search_count([
            ('model_name', '=', 'account.move'), ('action', '=', 'create')])
        move = self.init_invoice('out_invoice', products=[self.product_a])
        after = log_model.search_count([
            ('model_name', '=', 'account.move'), ('action', '=', 'create')])
        self.assertEqual(after, before + 1)
        log = log_model.search([
            ('model_name', '=', 'account.move'), ('res_id', '=', move.id),
            ('action', '=', 'create'),
        ])
        self.assertEqual(len(log), 1)

    def test_post_is_logged_as_state_change(self):
        move = self.init_invoice('out_invoice', products=[self.product_a])
        move.action_post()
        log = self.env['erp.colombia.audit.log'].search([
            ('model_name', '=', 'account.move'), ('res_id', '=', move.id),
            ('action', '=', 'state_change'), ('field_name', '=', 'state'),
        ])
        self.assertEqual(len(log), 1)
        self.assertEqual(log.old_value, 'draft')
        self.assertEqual(log.new_value, 'posted')

    def test_cancel_is_logged_as_state_change(self):
        move = self.init_invoice('out_invoice', products=[self.product_a])
        move.button_cancel()
        log = self.env['erp.colombia.audit.log'].search([
            ('model_name', '=', 'account.move'), ('res_id', '=', move.id),
            ('action', '=', 'state_change'), ('new_value', '=', 'cancel'),
        ])
        self.assertEqual(len(log), 1)
