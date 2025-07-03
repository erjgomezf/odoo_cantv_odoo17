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
        # Establece el almacén por defecto al primero encontrado o al almacén de la compañía actual
        user_company = self.env.company
        return self.env['stock.warehouse'].search([('company_id', '=', user_company.id)], limit=1)

    def print_report(self):
        """
        Método para imprimir el reporte de inventario con el almacén seleccionado.
        """
        self.ensure_one()

        # Obtenemos la ubicación principal del almacén seleccionado.
        # Los stock.quant (registros de inventario) están asociados a ubicaciones (stock.location),
        # no directamente a almacenes (stock.warehouse).
        # 'lot_stock_id' es la ubicación de stock por defecto de un almacén.
        location = self.warehouse_id.lot_stock_id

        # Preparamos los datos de contexto que se pasarán a la plantilla QWeb del reporte
        data = {
            'context': {
                'location_id': location.id,
                'location_name': location.display_name, # Nombre completo de la ubicación (ej. 'YourCompany/Stock')
            }
        }

        # Llamamos a la acción del reporte PDF que ya tienes definida.
        # 'self' se pasa como un pseudo-registro para que Odoo sepa de qué modelo se llama,
        # aunque los datos relevantes van en 'data'.
        return self.env.ref('cantv_inventory_ext.action_report_cantv_inventory').report_action(self, data=data)