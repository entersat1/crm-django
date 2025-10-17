from django.db import models
from django.utils import timezone
from clientes.models import Cliente
from inventario.models import Producto

class Venta(models.Model):
    ESTADO_CHOICES = [
        ('finalizada', 'Finalizada'),
        ('anulada', 'Anulada'),
    ]

    TIPO_COMPROBANTE_CHOICES = [
        ('A', 'Factura A'),
        ('B', 'Factura B'),
        ('C', 'Factura C'),
        ('T', 'Ticket'),
    ]

    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Cliente",
        related_name="ventas_taller"  # ← NUEVO: related_name único
    )
    fecha_venta = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Venta")
    cotizacion_dolar = models.DecimalField(max_digits=10, decimal_places=2, default=1405.00, verbose_name="Cotización del dólar")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total en Pesos")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='finalizada', verbose_name="Estado")
    tipo_comprobante = models.CharField(max_length=1, choices=TIPO_COMPROBANTE_CHOICES, default='C', verbose_name="Tipo de Comprobante")
    comprobante = models.CharField(max_length=50, blank=True, verbose_name="N° Comprobante")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']

    def __str__(self):
        nombre_cliente = self.cliente if self.cliente else "Venta de Mostrador"
        return f"Venta #{self.id} - {nombre_cliente} - {self.fecha_venta.strftime('%d/%m/%Y')}"

    def actualizar_total(self):
        total_calculado = self.detalles.aggregate(total=models.Sum('subtotal_en_pesos'))['total'] or 0
        if self.total != total_calculado:
            self.total = total_calculado
            self.save(update_fields=['total'])
        return self.total

    @property
    def whatsapp_link(self):
        if self.cliente and self.cliente.telefono:
            numero = ''.join(filter(str.isdigit, self.cliente.telefono))
            mensaje = f"Hola {self.cliente.nombre}, su venta #{self.id} fue registrada por ${self.total:.2f}."
            return f"https://wa.me/{numero}?text={mensaje}"
        return None

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE, verbose_name="Venta")
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.PROTECT, 
        verbose_name="Producto",
        related_name="detalles_venta_taller"  # ← NUEVO: related_name único
    )
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    precio_unitario_usd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario (USD)")
    descuento_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Descuento (USD)")
    subtotal_usd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal (USD)")
    subtotal_en_pesos = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal (Pesos)")

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    def save(self, *args, **kwargs):
        self.subtotal_usd = (self.precio_unitario_usd * self.cantidad) - self.descuento_usd
        self.subtotal_en_pesos = round(self.subtotal_usd * self.venta.cotizacion_dolar, 2)
        super().save(*args, **kwargs)
        self.venta.actualizar_total()