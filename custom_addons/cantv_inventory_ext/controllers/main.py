# -*- coding: utf-8 -*-
import io
import json
import base64
from odoo import http
from odoo.http import request, content_disposition

# Importaciones de Reportlab
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# Función para el encabezado y pie de página
def _header_footer(canvas, doc, location_name):
    canvas.saveState()
    
    # Dimensiones de la página A4 en horizontal
    page_width, page_height = landscape(A4) 

    # --- Encabezado ---
    # Logo - Asegúrate que esta ruta sea correcta para tu Odoo
    logo_path = 'http://localhost:8069/cantv_inventory_ext/static/src/img/cantv_logo.png' 
    try:
        logo = ImageReader(logo_path)
        # Posición del logo (ajustada para landscape y topMargin, y nuevo leftMargin)
        canvas.drawImage(logo, doc.leftMargin, page_height - doc.topMargin + 10, width=80, height=30, preserveAspectRatio=True)
    except Exception:
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(doc.leftMargin, page_height - doc.topMargin + 20, "LOGO CANTV (no encontrado)")

    # Información de la compañía (izquierda, ajustado a nuevo leftMargin)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(doc.leftMargin + 90, page_height - doc.topMargin + 25, "Compañía Anónima Nacional Teléfonos de Venezuela")
    canvas.setFont('Helvetica', 8)
    canvas.drawString(doc.leftMargin + 90, page_height - doc.topMargin + 15, "CANTV")
    canvas.drawString(doc.leftMargin + 90, page_height - doc.topMargin + 5, "Caracas, Venezuela")

    # Títulos del reporte (derecha, ajustado a nuevo rightMargin)
    canvas.setFont('Helvetica-Bold', 12)
    canvas.drawRightString(page_width - doc.rightMargin, page_height - doc.topMargin + 40, f"INVENTARIO DE MATERIALES/EQUIPOS DEL DEPÓSITO: {location_name}")
    canvas.setFont('Helvetica', 10)
    canvas.drawRightString(page_width - doc.rightMargin, page_height - doc.topMargin + 25, "CONTROL DE INVENTARIO DE MATERIALES Y EQUIPOS DE LA GERENCIA RED TRONCAL Y TRANSPORTE")
    canvas.drawRightString(page_width - doc.rightMargin, page_height - doc.topMargin + 10, "Gerencia General Proyectos Mayores")
    canvas.drawRightString(page_width - doc.rightMargin, page_height - doc.topMargin - 5, "Gerencia Programa Redes de Acceso")

    # Línea Separadora
    canvas.line(doc.leftMargin, page_height - doc.topMargin - 15, page_width - doc.rightMargin, page_height - doc.topMargin - 15)


    # --- Pie de página ---
    canvas.setFont('Helvetica', 8)
    # Centrado en el nuevo ancho de página
    canvas.drawCentredString(page_width / 2, doc.bottomMargin / 2, f"Página: {doc.page}") 
    canvas.restoreState()


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

        warehouse_name = location.warehouse_id.name if location.warehouse_id else 'N/A'

        buffer = io.BytesIO()
        
        # Ajusta los márgenes laterales a 1 cm (aproximadamente 0.39 pulgadas)
        doc = SimpleDocTemplate(buffer,
                                pagesize=landscape(A4), 
                                rightMargin=0.39*inch,  # Margen derecho a 1 cm (0.39 pulgadas)
                                leftMargin=0.39*inch,   # Margen izquierdo a 1 cm (0.39 pulgadas)
                                topMargin=1.5*inch,    
                                bottomMargin=0.75*inch) 
        
        styles = getSampleStyleSheet()

        # Ajustamos el tamaño de fuente para mejorar la legibilidad, si es posible.
        # Volvemos a 7 para el contenido y 8 para los encabezados, que es más estándar.
        styles.add(ParagraphStyle(name='TableContent', parent=styles['Normal'], fontSize=7, leading=9))
        styles.add(ParagraphStyle(name='TableHeader', parent=styles['Normal'], fontSize=8, fontName='Helvetica-Bold', alignment=1, leading=10))
        
        elements = []

        quants = request.env['stock.quant'].sudo().search([
            ('quantity', '>', 0),
            ('location_id', 'child_of', location.id),
            ('product_id.is_cantv_asset', '=', True)
        ])

        table_headers = [
            Paragraph("DESCRIPCIÓN DEL MATERIAL", styles['TableHeader']),
            Paragraph("UM", styles['TableHeader']),
            Paragraph("MARCA", styles['TableHeader']),
            Paragraph("MODELO", styles['TableHeader']),
            Paragraph("SERIAL", styles['TableHeader']),
            Paragraph("CODIGO DE MATERIAL SIR", styles['TableHeader']),
            Paragraph("COD INVENTARIO SAP", styles['TableHeader']),
            Paragraph("OBSERVACION", styles['TableHeader']),
            Paragraph("UBICACIÓN", styles['TableHeader']),
            Paragraph("INICIAL", styles['TableHeader']),
            Paragraph("ENTREGADO", styles['TableHeader']),
            Paragraph("DISPONIBLE", styles['TableHeader']),
            Paragraph("ALMACEN TRANSITORIO", styles['TableHeader'])
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
                Paragraph('', styles['TableContent']), # Placeholder para OBSERVACION
                Paragraph(quant.location_id.display_name or '', styles['TableContent']),
                Paragraph('', styles['TableContent']), # Placeholder para INICIAL
                Paragraph('', styles['TableContent']), # Placeholder para ENTREGADO
                Paragraph(str(quant.quantity), styles['TableContent']),
                Paragraph('', styles['TableContent']) # Placeholder para ALMACEN TRANSITORIO
            ])

        if table_data:
            # Anchos de columna ajustados para A4 Landscape con 1cm de márgenes (ancho utilizable aprox. 10.79 pulgadas)
            # Suma total de anchos: 1.8 + 0.4 + 0.7 + 0.7 + 0.9 + 0.8 + 0.8 + 1.0 + 1.0 + 0.6 + 0.6 + 0.5 + 0.9 = 10.7 pulgadas
            col_widths = [
                1.8*inch,  # DESCRIPCIÓN DEL MATERIAL
                0.4*inch,  # UM
                0.7*inch,  # MARCA
                0.7*inch,  # MODELO
                0.9*inch,  # SERIAL
                0.8*inch,  # CODIGO DE MATERIAL SIR
                0.8*inch,  # COD INVENTARIO SAP
                1.0*inch,  # OBSERVACION
                1.0*inch,  # UBICACIÓN
                0.6*inch,  # INICIAL
                0.6*inch,  # ENTREGADO
                0.5*inch,  # DISPONIBLE
                0.9*inch   # ALMACEN TRANSITORIO
            ]
            
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3F729B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (11,0), (11,-1), 'RIGHT'), # Columna "DISPONIBLE" (índice 11) a la derecha
                ('LEFTPADDING', (0,0), (-1,-1), 2),
                ('RIGHTPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,1), (-1,-1), 2),
                ('BOTTOMPADDING', (0,1), (-1,-1), 2),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No hay productos disponibles en este almacén con las características CANTV.", styles['Normal']))

        doc.build(elements, onFirstPage=lambda canvas, doc: _header_footer(canvas, doc, warehouse_name),
                            onLaterPages=lambda canvas, doc: _header_footer(canvas, doc, warehouse_name))
        
        pdf_content = buffer.getvalue()
        buffer.close()

        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', content_disposition(f'Inventario_CANTV_{location.name}.pdf'))
        ]
        return request.make_response(pdf_content, headers=headers)