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
    # Logo - Construimos la URL dinámicamente para que funcione en cualquier servidor
    base_url = request.httprequest.url_root
    logo_path = f'{base_url}cantv_inventory_ext/static/src/img/cantv_logo.png'
    try:
        logo = ImageReader(logo_path)
        # Posición del logo: lo más en el extremo superior izquierdo
        # Ajustamos el +Y para que no se pegue al borde superior absoluto pero esté muy cerca
        canvas.drawImage(logo, doc.leftMargin, page_height - doc.topMargin + 20, width=80, height=30, preserveAspectRatio=True)
        # Nota: El fondo blanco del logo debe ser parte del archivo de imagen (cantv_logo.png). 
        # Reportlab no puede cambiar el fondo de una imagen.
    except Exception:
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(doc.leftMargin, page_height - doc.topMargin + 20, "LOGO CANTV (no encontrado)")

    # Eliminadas: "Compañía Anónima Nacional Teléfonos de Venezuela", "CANTV", "Caracas, Venezuela"
    # Eliminadas: "Gerencia General Proyectos Mayores", "Gerencia Programa Redes de Acceso"

    # Títulos del reporte - Centrados horizontalmente
    # Ajustamos las coordenadas Y para que estén alineados y bien espaciados
    canvas.setFont('Helvetica-Bold', 12)
    canvas.drawCentredString(page_width / 2, page_height - doc.topMargin + 25, f"INVENTARIO DE MATERIALES/EQUIPOS DEL DEPÓSITO: {location_name}")
    canvas.setFont('Helvetica', 10)
    canvas.drawCentredString(page_width / 2, page_height - doc.topMargin + 10, "CONTROL DE INVENTARIO DE MATERIALES Y EQUIPOS DE LA GERENCIA RED TRONCAL Y TRANSPORTE")

    # Línea Separadora
    canvas.line(doc.leftMargin, page_height - doc.topMargin - 15, page_width - doc.rightMargin, page_height - doc.topMargin - 15)


    # --- Pie de página ---
    canvas.setFont('Helvetica', 8)
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
        
        # Ajusta los márgenes laterales a 0.25*inch (~0.635 cm)
        doc = SimpleDocTemplate(buffer,
                                pagesize=landscape(A4), 
                                rightMargin=0.25*inch,  
                                leftMargin=0.25*inch,   
                                topMargin=1.5*inch,    
                                bottomMargin=0.75*inch) 
        
        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(name='TableContent', parent=styles['Normal'], fontSize=6, leading=9))
        styles.add(ParagraphStyle(name='TableHeader', parent=styles['Normal'], fontSize=7, fontName='Helvetica-Bold', alignment=1, leading=10))
        
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
            Paragraph("UBICACIÓN ACTUAL", styles['TableHeader']),
            Paragraph("DISPONIBLE", styles['TableHeader'])
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
                Paragraph(product_tmpl.cantv_notes or '', styles['TableContent']), 
                Paragraph(quant.location_id.display_name or '', styles['TableContent']), 
                Paragraph(str(quant.quantity), styles['TableContent']) 
            ])

        if table_data:
            # Anchos de columna ajustados para un ancho útil de aprox. 11.19 pulgadas
            col_widths = [
                2.5*inch,  # DESCRIPCIÓN DEL MATERIAL
                0.7*inch,  # UM
                0.7*inch,  # MARCA
                0.7*inch,  # MODELO
                1.3*inch,  # SERIAL
                0.8*inch,  # CODIGO DE MATERIAL SIR
                0.8*inch,  # COD INVENTARIO SAP
                1.5*inch,  # OBSERVACION
                1.5*inch,  # UBICACIÓN ACTUAL
                0.7*inch   # DISPONIBLE
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
                ('ALIGN', (9,0), (9,-1), 'RIGHT'), # Columna "DISPONIBLE" (índice 9) a la derecha
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