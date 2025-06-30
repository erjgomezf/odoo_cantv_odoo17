{
    'name': "CANTV - Extensión de Inventario",
    'summary': "Campos y funcionalidades adicionales para la gestión de inventario de fibra óptica en CANTV.",
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'author': "Ernesto Gomez", # Nombre del desarrollador
    'website': "http://www.cantv.com.ve",
    'license': 'LGPL-3',
    'depends': ['stock', 'product'], # Esto es crucial
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml', # Archivo XML que define las vistas y campos adicionales
        'report/inventory_report.xml', # Reporte de inventario personalizado
        'report/inventory_report_templates.xml', # Plantillas del reporte de inventario
        'report/incoming_report_templates.xml', # Plantillas del reporte de entradas
        'views/stock_picking_views.xml', # Vistas para stock.picking
        'report/outgoing_report_templates.xml', # Plantillas del reporte de salidas
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}