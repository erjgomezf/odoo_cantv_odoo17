# cantv_inventory_ext/models/product_template_ext.py

from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template' # Estamos extendiendo el modelo 'product.template' (plantilla de producto)

    # Campos para el inventario de fibra óptica y activos de red
    is_cantv_asset = fields.Boolean(string="Es Activo CANTV", default=False, help="Indica si este producto es un activo físico rastreable por CANTV.")
    cantv_serial_number = fields.Char(string="Número de Serie CANTV", copy=False, help="Inventario corporativo de CANTV para rastrear el activo.") 
    cantv_acquisition_date = fields.Date(string="Fecha de Adquisición")
    cantv_estimated_lifespan = fields.Integer(string="Vida Útil Estimada (años)")
    cantv_asset_state = fields.Selection([
        ('new', 'Nuevo'),
        ('used', 'Usado'),
        ('damaged', 'Dañado'),
        ('repair', 'En Reparación'),
        ('disposed', 'Dado de Baja'),
    ], string="Estado del Activo", default='new', help="Estado actual del activo en la red de CANTV.")
    cantv_responsible_person = fields.Many2one('res.partner', string="Persona Responsable") # Persona de contacto

    # NUEVOS CAMPOS AÑADIDOS
    cantv_brand = fields.Char(string="Marca", help="Marca del activo de red o equipo de fibra óptica.")
    cantv_model = fields.Char(string="Modelo", help="Modelo del activo de red o equipo de fibra óptica.")
    cantv_material_sir_code = fields.Char(string="Código Material SIR", copy=False)
    cantv_sap_code = fields.Char(string="Código Inventario SAP", copy=False)

    cantv_notes = fields.Text(string="Observaciones") # Notas adicionales sobre el activo