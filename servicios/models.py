from django.db import models
import random
import string
from django.utils import timezone
from urllib.parse import quote
from configuracion.models import Empresa as ConfiguracionNegocio
from inventario.models import Producto  # ✅ IMPORTACIÓN CORRECTA

class OrdenTaller(models.Model):
    ESTADO_CHOICES = [
        ('recibido', 'Recibido'),
        ('diagnostico', 'En Diagnóstico'),
        ('presupuesto', 'Presupuesto Enviado'), 
        ('espera_repuesto', 'Esperando Repuesto'),
        ('reparacion', 'En Reparación'),
        ('completado', 'Completado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('normal', 'Normal'),
        ('alta', 'Alta'), 
        ('urgente', 'Urgente'),
    ]

    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, verbose_name="Cliente")
    equipo = models.CharField(max_length=200, verbose_name="Equipo/Marca/Modelo")
    problema = models.TextField(verbose_name="Problema reportado")
    diagnostico = models.TextField(blank=True, verbose_name="Diagnóstico técnico")
    solucion = models.TextField(blank=True, verbose_name="Solución aplicada")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='recibido')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='normal')
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    fecha_prometida = models.DateField(null=True, blank=True, verbose_name="Fecha prometida")
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Presupuesto")
    costo_final = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo final")
    seña = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Seña")
    numero_serie = models.CharField(max_length=100, blank=True, verbose_name="Número de Serie")
    accesorios = models.TextField(blank=True, verbose_name="Accesorios que ingresan")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    codigo_consulta = models.CharField(
        max_length=10, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="Código de Consulta WhatsApp"
    )

    class Meta:
        verbose_name = "Orden de Taller"
        verbose_name_plural = "Órdenes de Taller"
        ordering = ['-fecha_ingreso']
    
    def __str__(self):
        return f"OT-{self.id:04d} - {self.cliente.nombre} - {self.equipo}"

    def save(self, *args, **kwargs):
        if not self.codigo_consulta:
            # Generar código alfanumérico simple de 6 caracteres
            while True:
                caracteres = string.ascii_uppercase + string.digits
                codigo = ''.join(random.choices(caracteres, k=6))
                # Quitar caracteres confusos
                codigo = codigo.replace('0', 'A').replace('1', 'B').replace('O', 'C').replace('I', 'D')
                if not OrdenTaller.objects.filter(codigo_consulta=codigo).exists():
                    self.codigo_consulta = codigo
                    break
        super().save(*args, **kwargs)
    
    @property
    def url_consulta_whatsapp(self):
        if self.codigo_consulta and hasattr(self, 'cliente'):
            config = ConfiguracionNegocio.objects.first()
            if config and config.telefono:
                mensaje = f"Hola! Quiero consultar el estado de mi orden. Código: {self.codigo_consulta}"
                telefono_limpio = ''.join(c for c in config.telefono if c.isdigit())
                return f"https://wa.me/{telefono_limpio}?text={quote(mensaje)}"
        return "#"

    @property
    def numero_orden(self):
        return f"OT-{self.id:04d}"

# ✅ ELIMINAR ProductoReparacion - REPLACE con ItemReparacion
class ItemReparacion(models.Model):
    orden = models.ForeignKey(OrdenTaller, on_delete=models.CASCADE, related_name='repuestos_usados')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto del Stock")
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad usada")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    
    class Meta:
        verbose_name = "Repuesto Usado"
        verbose_name_plural = "Repuestos Usados"
    
    def save(self, *args, **kwargs):
        # Al guardar, descontar del stock automáticamente
        if not self.pk:  # Solo si es nuevo (no en updates)
            if self.producto.stock_actual >= self.cantidad:
                self.producto.stock_actual -= self.cantidad
                self.producto.save()
            else:
                raise ValueError(f"Stock insuficiente: {self.producto.nombre}")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - {self.orden.numero_orden}"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario