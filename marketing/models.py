from django.db import models
from clientes.models import Cliente
from django.contrib.auth.models import User

class CampanaMarketing(models.Model):
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Campaña")
    asunto = models.CharField(max_length=200, blank=True, help_text="Solo para campañas de Email")
    contenido = models.TextField(verbose_name="Cuerpo del Mensaje")
    segmento_clientes = models.ManyToManyField(Cliente, blank=True, verbose_name="Enviar a Clientes")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
