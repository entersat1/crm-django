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
            return True
        except Exception as e:
            logger.error(f"Error enviando email a {destinatario}: {e}")
            return False

class PDFService:
    @staticmethod
    def generar_pdf_orden_servicio(orden):
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=inch, bottomMargin=inch)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph(f"Orden de Servicio #{orden.numero_orden or orden.id}", styles['h1']))
            # Aquí va toda la lógica para dibujar el PDF...
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Error generando PDF para orden {orden.id}: {e}")
            return None
        # Agrega al final de tu settings.py
# =============================================================================
# CONFIGURACIÓN PARA EMAIL, WHATSAPP E IMPRESIÓN
# =============================================================================

# Configuración de Empresa
EMPRESA_NOMBRE = "Mi Taller"
EMPRESA_DIRECCION = "Tu dirección aquí"
EMPRESA_TELEFONO = "+54 9 11 1234-5678"
EMPRESA_EMAIL = "tallermecanico@empresa.com"

# WhatsApp Business API (opcional)
WHATSAPP_NUMERO = "5491112345678"  # Número en formato internacional sin +

# Configuración de Email para Producción (descomenta cuando estés listo)
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # o tu servidor SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-password'
"""

# Instalar WeasyPrint para generación de PDFs
# pip install weasyprint