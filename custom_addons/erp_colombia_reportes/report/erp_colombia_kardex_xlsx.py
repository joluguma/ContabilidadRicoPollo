# Part of ERP Colombia. See LICENSE file for full copyright and licensing details.
from odoo import models


class ErpColombiaKardexXlsx(models.AbstractModel):
    _name = 'report.erp_colombia_reportes.erp_colombia_kardex_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'ERP Colombia - Kardex (Excel)'

    def generate_xlsx_report(self, workbook, data, wizards):
        for wizard in wizards:
            sheet = workbook.add_worksheet(wizard.product_id.default_code or 'Kardex')
            bold = workbook.add_format({'bold': True})
            money_fmt = workbook.add_format({'num_format': '#,##0.00'})
            title = f"Kardex - {wizard.product_id.display_name}"
            if wizard.warehouse_id:
                title += f" - {wizard.warehouse_id.name}"
            sheet.merge_range(0, 0, 0, 9, title, bold)
            sheet.write(
                1, 0,
                f"Del {wizard.date_from} al {wizard.date_to}"
                f" - Saldo inicial: {wizard.saldo_inicial_cantidad}"
                f" ({wizard.saldo_inicial_valor})",
            )

            headers = [
                'Fecha', 'Documento', 'Tipo movimiento', 'Bodega',
                'Entrada', 'Salida', 'Saldo', 'Costo unitario',
                'Costo total', 'Saldo (valor)',
            ]
            for col, header in enumerate(headers):
                sheet.write(3, col, header, bold)

            row = 4
            for line in wizard.line_ids:
                sheet.write(row, 0, str(line.date) if line.date else '')
                sheet.write(row, 1, line.document or '')
                sheet.write(row, 2, line.move_type or '')
                sheet.write(row, 3, line.warehouse or '')
                sheet.write(row, 4, line.entrada, money_fmt)
                sheet.write(row, 5, line.salida, money_fmt)
                sheet.write(row, 6, line.saldo_cantidad, money_fmt)
                sheet.write(row, 7, line.costo_unitario, money_fmt)
                sheet.write(row, 8, line.costo_total, money_fmt)
                sheet.write(row, 9, line.saldo_valor, money_fmt)
                row += 1

            sheet.set_column(0, 0, 18)
            sheet.set_column(1, 2, 22)
            sheet.set_column(3, 9, 16)
