# cantv_inventory_ext/models/stock_picking.py

from odoo import fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Campos para el informe de Salidas
    cantv_solicited_by = fields.Char(string='Solicitado Por')
    cantv_retrieved_by = fields.Char(string='Retirado Por')
    cantv_unit = fields.Char(string='Unidad')
    cantv_project = fields.Char(string='Proyecto Ampliacion') # Cambié el nombre para que coincida con tu plantilla
    
