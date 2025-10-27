import logging
from io import BytesIO
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

logger = logging.getLogger(__name__)

class NotificacionesService:
    @staticmethod
    def enviar_email(destinatario, asunto, template, contexto, archivo_adjunto=None):
        """
        Envía un email con template HTML y opcionalmente un archivo adjunto
        """
        try:
            html_content = render_to_string(template, contexto)
            email = EmailMessage(
                subject=asunto,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destinatario]
            )
            email.content_subtype = "html"
            
            if archivo_adjunto:
                email.attach(
                    archivo_adjunto.get('nombre', 'documento.pdf'),
                    archivo_adjunto.get('contenido'),
                    archivo_adjunto.get('tipo', 'application/pdf')
                )
            
            email.send(fail_silently=False)
            logger.info(f"✅ Email enviado exitosamente a {destinatario}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando email a {destinatario}: {str(e)}")
            return False

    @staticmethod
    def enviar_notificacion_whatsapp(numero, mensaje):
        """
        Envía una notificación por WhatsApp (requiere configuración de API)
        """
        try:
            # Implementación básica - extender con API de WhatsApp Business
            logger.info(f"📱 Notificación WhatsApp para {numero}: {mensaje}")
            return True
        except Exception as e:
            logger.error(f"❌ Error enviando WhatsApp: {str(e)}")
            return False

class PDFService:
    @staticmethod
    def generar_pdf_orden_servicio(orden):
        """
        Genera un PDF profesional para órdenes de servicio
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4, 
                topMargin=0.5*inch, 
                bottomMargin=0.5*inch,
                leftMargin=0.5*inch,
                rightMargin=0.5*inch
            )
            
            styles = getSampleStyleSheet()
            story = []

            # Encabezado
            title_style = styles['Heading1']
            title_style.alignment = 1  # Centrado
            story.append(Paragraph("ORDEN DE SERVICIO", title_style))
            story.append(Spacer(1, 0.2*inch))

            # Información de la orden
            story.append(Paragraph(f"<b>Número de Orden:</b> {orden.numero_orden}", styles['Normal']))
            story.append(Paragraph(f"<b>Fecha:</b> {orden.fecha_ingreso.strftime('%d/%m/%Y')}", styles['Normal']))
            story.append(Paragraph(f"<b>Cliente:</b> {orden.cliente.nombre}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

            # Información del equipo
            story.append(Paragraph("<b>INFORMACIÓN DEL EQUIPO</b>", styles['Heading2']))
            story.append(Paragraph(f"<b>Equipo:</b> {orden.equipo}", styles['Normal']))
            if orden.numero_serie:
                story.append(Paragraph(f"<b>Número de Serie:</b> {orden.numero_serie}", styles['Normal']))
            story.append(Paragraph(f"<b>Problema reportado:</b> {orden.problema}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

            # Diagnóstico y solución
            if orden.diagnostico:
                story.append(Paragraph("<b>DIAGNÓSTICO</b>", styles['Heading2']))
                story.append(Paragraph(orden.diagnostico, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))

            if orden.solucion:
                story.append(Paragraph("<b>SOLUCIÓN APLICADA</b>", styles['Heading2']))
                story.append(Paragraph(orden.solucion, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))

            # Información económica
            story.append(Paragraph("<b>INFORMACIÓN ECONÓMICA</b>", styles['Heading2']))
            
            # Calcular totales
            costo_repuestos = sum(item.subtotal for item in orden.repuestos_usados.all())
            costo_total = orden.costo_final + costo_repuestos
            
            data = [
                ['Concepto', 'Monto'],
                ['Mano de obra', f"${orden.costo_final:.2f}"],
                ['Repuestos', f"${costo_repuestos:.2f}"],
                ['TOTAL', f"<b>${costo_total:.2f}</b>"]
            ]
            
            table = Table(data, colWidths=[3*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))

            # Pie de página
            story.append(Paragraph("<i>Documento generado automáticamente - Sistema de Gestión de Taller</i>", styles['Italic']))

            # Construir el PDF
            doc.build(story)
            buffer.seek(0)
            
            logger.info(f"✅ PDF generado exitosamente para orden {orden.numero_orden}")
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error generando PDF para orden {orden.id}: {str(e)}")
            return None

    @staticmethod
    def generar_pdf_presupuesto(orden):
        """
        Genera un PDF de presupuesto para aprobación del cliente
        """
        try:
            # Implementación similar a generar_pdf_orden_servicio pero para presupuestos
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph(f"PRESUPUESTO - Orden #{orden.numero_orden}", styles['h1']))
            story.append(Spacer(1, 0.2*inch))
            
            # Contenido del presupuesto...
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error generando presupuesto PDF: {str(e)}")
            return None

# Configuración adicional para el módulo
CONFIG_EMPRESA = {
    'nombre': getattr(settings, 'EMPRESA_NOMBRE', 'Mi Taller'),
    'direccion': getattr(settings, 'EMPRESA_DIRECCION', 'Dirección no configurada'),
    'telefono': getattr(settings, 'EMPRESA_TELEFONO', '+54 9 11 1234-5678'),
    'email': getattr(settings, 'EMPRESA_EMAIL', 'taller@empresa.com')
}