# -*- coding: utf-8 -*-
import io
import json
import base64
from odoo import http
from odoo.http import request, content_disposition

# Importaciones de Reportlab
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

class CantvInventoryReportController(http.Controller):
    # Define la ruta a la que tu asistente llamará
    @http.route('/cantv_inventory_ext/report/pdf', type='http', auth='user', website=False)
    def generate_cantv_inventory_pdf(self, location_id, **kw):
        # Asegúrate de que location_id es un entero
        try:
            location_id = int(location_id)
        except ValueError:
            return request.not_found()

        # Obtener el registro de la ubicación
        location = request.env['stock.location'].sudo().browse(location_id)
        if not location.exists():
            return request.not_found()

        # --- Lógica de Reportlab para generar el PDF ---
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter) # O A4 si prefieres
        styles = getSampleStyleSheet()
        elements = []

        # Título principal del reporte
        elements.append(Paragraph(f"CONTROL DE INVENTARIO DE MATERIALES Y EQUIPOS DEL ALMACÉN:", styles['h1']))
        elements.append(Paragraph(f"<font color='blue'>{location.display_name}</font>", styles['h2'])) # Nombre del almacén en azul
        elements.append(Spacer(1, 0.2 * inch)) # Espacio

        # Obtener los datos (la misma consulta que antes)
        quants = request.env['stock.quant'].sudo().search([
            ('quantity', '>', 0),
            ('location_id', 'child_of', location.id), # Buscar en la ubicación y sus hijos
            ('product_id.is_cantv_asset', '=', True) # Asegúrate que este campo existe
        ])

        # Preparar los datos para la tabla de Reportlab
        table_data = [
            ['Descripción', 'UM', 'Marca', 'Modelo', 'Serial', 'Cod SIR', 'Cod SAP', 'Ubicación', 'Disp.']
        ]
        for quant in quants:
            product_tmpl = quant.product_tmpl_id
            table_data.append([
                product_tmpl.name or '',
                product_tmpl.uom_id.name or '',
                product_tmpl.cantv_brand or '',
                product_tmpl.cantv_model or '',
                quant.lot_id.name if quant.lot_id else product_tmpl.cantv_serial_number or '', # Asumiendo serial puede ser lot_id o campo en producto
                product_tmpl.cantv_material_sir_code or '',
                product_tmpl.cantv_sap_code or '',
                quant.location_id.display_name or '',
                str(quant.quantity)
            ])

        if table_data:
            table = Table(table_data, colWidths=[1.5*inch, 0.5*inch, 1*inch, 1*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1.2*inch, 0.6*inch]) # Ancho de columnas
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3F729B')), # Encabezado azul oscuro
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')), # Filas alternas si quieres
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')), # Rejilla gris claro
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (-1,0), (-1,-1), 'RIGHT'), # Columna Disponible a la derecha
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No hay productos disponibles en este almacén con las características CANTV.", styles['Normal']))

        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()

        # --- Devolver el PDF como una respuesta HTTP ---
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', content_disposition(f'Inventario_CANTV_{location.name}.pdf'))
        ]
        return request.make_response(pdf_content, headers=headers)