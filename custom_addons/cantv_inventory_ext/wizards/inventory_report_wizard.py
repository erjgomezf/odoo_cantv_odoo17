# -*- coding: utf-8 -*-
# cantv_inventory_ext/wizards/inventory_report_wizard.py

from odoo import models, fields, api

class CantvInventoryReportWizard(models.TransientModel):
    _name = 'cantv.inventory.report.wizard'
    _description = 'Asistente para Reporte de Inventario CANTV'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string="Almacén",
        required=True,
        default=lambda self: self._get_default_warehouse(),
        help="Seleccione el almacén para generar el reporte de inventario."
    )

    @api.model
    def _get_default_warehouse(self):
        user_company = self.env.company
        return self.env['stock.warehouse'].search([('company_id', '=', user_company.id)], limit=1)

    def print_report(self):
        """
        Método para imprimir el reporte de inventario con el almacén seleccionado,
        usando un controlador HTTP para generar el PDF con Reportlab.
        """
        self.ensure_one()
        location = self.warehouse_id.lot_stock_id

        # Redirigir al navegador a la URL de nuestro controlador
        return {
            'type': 'ir.actions.act_url',
            'url': f'/cantv_inventory_ext/report/pdf?location_id={location.id}',
            'target': 'new', # Abre el PDF en una nueva pestaña
        }