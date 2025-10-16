from django.db import models
from clientes.models import Cliente

class Equipo(models.Model):
    TIPOS_EQUIPO = [
        ('laptop', 'Laptop'),
        ('pc', 'Computadora de Escritorio'),
        ('impresora', 'Impresora'),
        ('monitor', 'Monitor'),
        ('telefono', 'Telefono'),
        ('tablet', 'Tablet'),
        ('otros', 'Otros'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del equipo")
    modelo = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS_EQUIPO, default='laptop')
    numero_serie = models.CharField(max_length=100, unique=True, blank=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='equipos')
    descripcion = models.TextField(blank=True, verbose_name="Descripcion adicional")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.modelo} ({self.cliente.nombre})"