# -*- coding: utf-8 -*-
import io
import json
import base64
from odoo import http
from odoo.http import request, content_disposition

# Importaciones de Reportlab
from reportlab.lib.pagesizes import letter, A4 # <<-- Aquí: A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class CantvInventoryReportController(http.Controller):
    @http.route('/cantv_inventory_ext/report/pdf', type='http', auth='user', website=False)
    def generate_cantv_inventory_pdf(self, location_id, **kw):
        try:
            location_id = int(location_id)
        except ValueError:
            return request.not_found()

        location = request.env['stock.location'].sudo().browse(location_id)
        if not location.exists():
            return request.not_found()

        buffer = io.BytesIO()
        # Cambia pagesize=letter a pagesize=A4
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        # Define un estilo para el texto de la tabla (más pequeño y justificado)
        styles.add(ParagraphStyle(name='TableContent', parent=styles['Normal'], fontSize=8, leading=10))
        styles.add(ParagraphStyle(name='TableHeader', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold', alignment=1)) # Centrado para encabezados
        
        elements = []

        # Título principal del reporte
        elements.append(Paragraph(f"CONTROL DE INVENTARIO DE MATERIALES Y EQUIPOS DEL ALMACÉN:", styles['h1']))
        elements.append(Paragraph(f"<font color='blue'>{location.display_name}</font>", styles['h2']))
        elements.append(Spacer(1, 0.2 * inch))

        quants = request.env['stock.quant'].sudo().search([
            ('quantity', '>', 0),
            ('location_id', 'child_of', location.id),
            ('product_id.is_cantv_asset', '=', True)
        ])

        # Preparar los datos para la tabla de Reportlab
        # Usamos Paragraph para los campos que puedan tener texto largo y necesiten envolverse
        table_headers = [
            Paragraph("Descripción", styles['TableHeader']),
            Paragraph("UM", styles['TableHeader']),
            Paragraph("Marca", styles['TableHeader']),
            Paragraph("Modelo", styles['TableHeader']),
            Paragraph("Serial", styles['TableHeader']),
            Paragraph("Cod SIR", styles['TableHeader']),
            Paragraph("Cod SAP", styles['TableHeader']),
            Paragraph("Ubicación", styles['TableHeader']),
            Paragraph("Disp.", styles['TableHeader'])
        ]
        table_data = [table_headers]

        for quant in quants:
            product_tmpl = quant.product_tmpl_id
            table_data.append([
                Paragraph(product_tmpl.name or '', styles['TableContent']),
                Paragraph(product_tmpl.uom_id.name or '', styles['TableContent']),
                Paragraph(product_tmpl.cantv_brand or '', styles['TableContent']),
                Paragraph(product_tmpl.cantv_model or '', styles['TableContent']),
                Paragraph(quant.lot_id.name if quant.lot_id else product_tmpl.cantv_serial_number or '', styles['TableContent']),
                Paragraph(product_tmpl.cantv_material_sir_code or '', styles['TableContent']),
                Paragraph(product_tmpl.cantv_sap_code or '', styles['TableContent']),
                Paragraph(quant.location_id.display_name or '', styles['TableContent']),
                Paragraph(str(quant.quantity), styles['TableContent']) # Cantidad se alinea a la derecha en el estilo
            ])

        if table_data:
            # Ajustar colWidths para A4 (aprox. 6.5 pulgadas de ancho utilizable con márgenes de 1 pulgada)
            # Suma de anchos: 1.5+0.5+0.8+0.8+1.0+0.7+0.7+1.0+0.6 = 7.6 pulgadas, un poco más apretado, pero mejor para envolver.
            # Podrías necesitar ajustar estos anchos para tu contenido específico.
            col_widths = [1.5*inch, 0.5*inch, 0.8*inch, 0.8*inch, 1.0*inch, 0.7*inch, 0.7*inch, 1.0*inch, 0.6*inch]
            
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3F729B')), # Encabezado azul oscuro
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'), # Alineación general a la izquierda
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8), # Reducir padding de encabezado
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')), # Filas alternas si quieres
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')), # Rejilla gris claro
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (8,0), (8,-1), 'RIGHT'), # Columna "Disp." (índice 8) a la derecha
                ('LEFTPADDING', (0,0), (-1,-1), 3), # Pequeño padding a la izquierda en las celdas
                ('RIGHTPADDING', (0,0), (-1,-1), 3), # Pequeño padding a la derecha en las celdas
                ('TOPPADDING', (0,1), (-1,-1), 3),
                ('BOTTOMPADDING', (0,1), (-1,-1), 3),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No hay productos disponibles en este almacén con las características CANTV.", styles['Normal']))

        doc.build(elements)
        pdf_content = buffer.getvalue()
        buffer.close()

        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', content_disposition(f'Inventario_CANTV_{location.name}.pdf'))
        ]
        return request.make_response(pdf_content, headers=headers)