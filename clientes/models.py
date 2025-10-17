from django.db import models

class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('persona', 'Persona Fisica'),
        ('empresa', 'Empresa'),
    ]

    IVA_CONDICION_CHOICES = [
        ('responsable_inscripto', 'Responsable Inscripto'),
        ('monotributista', 'Monotributista'),
        ('exento', 'Exento'),
        ('no_responsable', 'No Responsable'),
        ('consumidor_final', 'Consumidor Final'),
    ]

    # --- Datos Personales / Empresa ---
    tipo_cliente = models.CharField(
        max_length=10, choices=TIPO_CLIENTE_CHOICES, default='persona', verbose_name="Tipo de cliente"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre o Razon Social")
    apellido = models.CharField(max_length=100, blank=True, verbose_name="Apellido (si es persona)")
    
    # --- Datos Fiscales ---
    condicion_iva = models.CharField(
        max_length=30, choices=IVA_CONDICION_CHOICES, default='consumidor_final', verbose_name="Condicion frente al IVA"
    )
    cuit = models.CharField(max_length=13, blank=True, verbose_name="CUIT/CUIL")

    # --- Datos de Contacto y Domicilio (CORREGIDOS) ---
    email = models.EmailField(blank=True, verbose_name="Email")
    telefono = models.CharField(max_length=50, blank=True, verbose_name="Telefono / WhatsApp")
    domicilio = models.CharField(max_length=255, blank=True, verbose_name="Domicilio") # <-- HECHO NO OBLIGATORIO
    ciudad = models.CharField(max_length=100, blank=True, verbose_name="Ciudad") # <-- AnADIDO
    provincia = models.CharField(max_length=100, blank=True, verbose_name="Provincia") # <-- AnADIDO
    
    # --- Otros Datos ---
    observaciones = models.TextField(blank=True, verbose_name="Notas internas")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellido', 'nombre']

    def __str__(self):
        if self.apellido:
            return f"{self.apellido}, {self.nombre}"
        return self.nombre

    @property
    def whatsapp_link(self):
        numero = ''.join(filter(str.isdigit, self.telefono))
        if numero:
            if not numero.startswith('54'):
                numero = '54' + numero
            return f"https://wa.me/{numero}"
        return None