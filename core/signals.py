<<<<<<< HEAD
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from servicios.models import OrdenTaller
from .services import NotificacionesService, PDFService

@receiver(pre_save, sender=OrdenTaller)
def guardar_estado_anterior(sender, instance, **kwargs):
    """
    Antes de que se guarde una orden, si ya existe, adjuntamos su estado
    anterior a la instancia para poder compararlo después.
    """
    if instance.pk:
        try:
            orden_anterior = OrdenTaller.objects.get(pk=instance.pk)
            instance._estado_anterior = orden_anterior.estado
        except OrdenTaller.DoesNotExist:
            instance._estado_anterior = None

@receiver(post_save, sender=OrdenTaller)
def notificar_cambios_orden(sender, instance, created, **kwargs):
    """
    Se ejecuta cuando se crea o actualiza una OrdenTaller para enviar notificaciones.
    """
    try:
        identificador_orden = instance.numero_orden or f"ID-{instance.id}"
        estado_anterior = getattr(instance, '_estado_anterior', None)
        estado_actual = instance.estado

        # Notificación para una orden nueva
        if created:
            asunto = f"Nueva Orden de Servicio #{identificador_orden}"
            template = 'emails/nueva_orden.html'
            contexto = {'orden': instance}
            pdf_content = PDFService.generar_pdf_orden_servicio(instance)
            adjunto = {'nombre': f'orden_{identificador_orden}.pdf', 'contenido': pdf_content, 'tipo': 'application/pdf'}
            
            if instance.cliente and instance.cliente.email:
                NotificacionesService.enviar_email(instance.cliente.email, asunto, template, contexto, adjunto)

        # Notificación para un cambio de estado en una orden existente
        elif estado_anterior != estado_actual:
            if estado_actual == 'finalizado':
                asunto = f"✅ Su Orden #{identificador_orden} ha sido Finalizada"
                template = 'emails/orden_finalizada.html'
            else:
                return # No enviamos email para otros estados intermedios
            
            contexto = {'orden': instance}
            if instance.cliente and instance.cliente.email:
                NotificacionesService.enviar_email(instance.cliente.email, asunto, template, contexto)

    except Exception as e:
=======
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from servicios.models import OrdenTaller
from .services import NotificacionesService, PDFService

@receiver(pre_save, sender=OrdenTaller)
def guardar_estado_anterior(sender, instance, **kwargs):
    """
    Antes de que se guarde una orden, si ya existe, adjuntamos su estado
    anterior a la instancia para poder compararlo después.
    """
    if instance.pk:
        try:
            orden_anterior = OrdenTaller.objects.get(pk=instance.pk)
            instance._estado_anterior = orden_anterior.estado
        except OrdenTaller.DoesNotExist:
            instance._estado_anterior = None

@receiver(post_save, sender=OrdenTaller)
def notificar_cambios_orden(sender, instance, created, **kwargs):
    """
    Se ejecuta cuando se crea o actualiza una OrdenTaller para enviar notificaciones.
    """
    try:
        identificador_orden = instance.numero_orden or f"ID-{instance.id}"
        estado_anterior = getattr(instance, '_estado_anterior', None)
        estado_actual = instance.estado

        # Notificación para una orden nueva
        if created:
            asunto = f"Nueva Orden de Servicio #{identificador_orden}"
            template = 'emails/nueva_orden.html'
            contexto = {'orden': instance}
            pdf_content = PDFService.generar_pdf_orden_servicio(instance)
            adjunto = {'nombre': f'orden_{identificador_orden}.pdf', 'contenido': pdf_content, 'tipo': 'application/pdf'}
            
            if instance.cliente and instance.cliente.email:
                NotificacionesService.enviar_email(instance.cliente.email, asunto, template, contexto, adjunto)

        # Notificación para un cambio de estado en una orden existente
        elif estado_anterior != estado_actual:
            if estado_actual == 'finalizado':
                asunto = f"✅ Su Orden #{identificador_orden} ha sido Finalizada"
                template = 'emails/orden_finalizada.html'
            else:
                return # No enviamos email para otros estados intermedios
            
            contexto = {'orden': instance}
            if instance.cliente and instance.cliente.email:
                NotificacionesService.enviar_email(instance.cliente.email, asunto, template, contexto)

    except Exception as e:
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
        print(f"❌ Error en la señal de notificación para orden #{instance.id}: {e}")