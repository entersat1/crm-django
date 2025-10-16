from django.db import models

class Empresa(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del negocio")
    cuit = models.CharField(max_length=20, verbose_name="CUIT")
    direccion = models.CharField(max_length=200, verbose_name="Dirección fiscal")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="Logo del negocio")
    cotizacion_dolar = models.DecimalField(max_digits=10, decimal_places=2, default=1405.00, verbose_name="Cotización del dólar")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Datos del negocio"

    def __str__(self):
        return self.nombre
