<<<<<<< HEAD
# models.py - VERSIÓN CORREGIDA
from django.db import models
from django.utils import timezone

class RubroGasto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    tipo = models.CharField(max_length=20, choices=[
        ('FIJO', 'Gasto Fijo'),
        ('VARIABLE', 'Gasto Variable'),
        ('EXTRA', 'Gasto Extraordinario')
    ], default='FIJO')
    
    class Meta:
        verbose_name = 'Rubro de Gasto'
        verbose_name_plural = 'Rubros de Gastos'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class Proveedor(models.Model):
    TIPOS = [
        ('MONOTRIBUTO', 'Monotributista'),
        ('RESPONSABLE', 'Responsable Inscripto'),
        ('EXENTO', 'Exento'),
        ('CONSUMIDOR', 'Consumidor Final')
    ]
    
    nombre = models.CharField(max_length=200)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # DATOS FISCALES
    cuit = models.CharField(max_length=13, blank=True, help_text="Formato: 20-12345678-9")
    tipo_iva = models.CharField(max_length=20, choices=TIPOS, default='RESPONSABLE')
    direccion = models.TextField(blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    # DATOS COMERCIALES
    plazo_garantia = models.PositiveIntegerField(
        default=12, 
        help_text="Meses de garantía por defecto"
    )
    condiciones_garantia = models.TextField(
        blank=True, 
        help_text="Términos y condiciones de la garantía"
    )
    contacto_garantias = models.CharField(max_length=100, blank=True)
    telefono_garantias = models.CharField(max_length=20, blank=True)
    
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True, help_text="Observaciones internas")
    
    class Meta:
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def compras_realizadas(self):
        return self.compramercaderia_set.count()
    
    def total_compras(self):
        from django.db.models import Sum
        result = self.compramercaderia_set.aggregate(total=Sum('total'))
        return result['total'] or 0

class CompraMercaderia(models.Model):
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado')
    ]
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha_compra = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    numero_factura = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR')
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Compra de Mercadería'
        verbose_name_plural = 'Compras de Mercadería'
    
    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor}"

class ItemCompra(models.Model):
    compra = models.ForeignKey(CompraMercaderia, on_delete=models.CASCADE, related_name='items')
    producto = models.CharField(max_length=200)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Item de Compra'
        verbose_name_plural = 'Items de Compra'
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

# ⬇️ CORREGIDO: MODELOS DE GARANTÍA
class ProductoConGarantia(models.Model):
    ESTADOS_GARANTIA = [
        ('VIGENTE', 'Garantía Vigente'),
        ('VENCIDA', 'Garantía Vencida'),
        ('EN_PROCESO', 'En Proceso de Garantía'),
        ('FINALIZADA', 'Garantía Finalizada')
    ]
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    compra = models.ForeignKey(CompraMercaderia, on_delete=models.CASCADE)
    producto = models.CharField(max_length=200)
    modelo = models.CharField(max_length=100, blank=True)
    numero_serie = models.CharField(max_length=100, blank=True)
    
    # DATOS DE GARANTÍA
    fecha_compra = models.DateField(default=timezone.now)  # ⬅️ Agregué default
    fecha_inicio_garantia = models.DateField(default=timezone.now)  # ⬅️ Agregué default
    fecha_fin_garantia = models.DateField(blank=True, null=True)  # ⬅️ Permite null
    meses_garantia = models.PositiveIntegerField(default=12)
    estado_garantia = models.CharField(max_length=20, choices=ESTADOS_GARANTIA, default='VIGENTE')
    
    # INFORMACIÓN ADICIONAL
    numero_factura = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Producto con Garantía'
        verbose_name_plural = 'Productos con Garantía'
    
    def __str__(self):
        return f"{self.producto} - {self.numero_serie or 'Sin serie'}"
    
    def dias_restantes_garantia(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        
        # ⬇️ CORRECCIÓN: Verificar que fecha_fin_garantia no sea None
        if not self.fecha_fin_garantia:
            return "No definida"
        
        if hoy > self.fecha_fin_garantia:
            return 0
        return (self.fecha_fin_garantia - hoy).days
    
    def save(self, *args, **kwargs):
        # ⬇️ CORRECCIÓN: Calcular fecha fin SIEMPRE que haya fecha_inicio
        if self.fecha_inicio_garantia and not self.fecha_fin_garantia:
            from datetime import timedelta
            self.fecha_fin_garantia = self.fecha_inicio_garantia + timedelta(days=self.meses_garantia * 30)
        
        # ⬇️ CORRECCIÓN: Solo actualizar estado si fecha_fin existe
        if self.fecha_fin_garantia:
            from django.utils import timezone
            hoy = timezone.now().date()
            if hoy > self.fecha_fin_garantia:
                self.estado_garantia = 'VENCIDA'
            elif self.estado_garantia == 'VENCIDA' and hoy <= self.fecha_fin_garantia:
                self.estado_garantia = 'VIGENTE'
            
        super().save(*args, **kwargs)

class ReclamoGarantia(models.Model):
    ESTADOS_RECLAMO = [
        ('INGRESADO', 'Reclamo Ingresado'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADO', 'Garantía Aprobada'),
        ('RECHAZADO', 'Garantía Rechazada'),
        ('REPARADO', 'Producto Reparado'),
        ('REEMPLAZADO', 'Producto Reemplazado'),
        ('FINALIZADO', 'Reclamo Finalizado')
    ]
    
    producto = models.ForeignKey(ProductoConGarantia, on_delete=models.CASCADE)
    fecha_reclamo = models.DateField(default=timezone.now)
    numero_reclamo = models.CharField(max_length=50, blank=True)  # ⬅️ Cambié unique=True por blank=True
    
    # DATOS DEL RECLAMO
    descripcion_problema = models.TextField()
    sintomas = models.TextField(blank=True, help_text="Qué falla presenta el producto")
    accesorios_entregados = models.TextField(blank=True, help_text="Accesorios que se entregaron con el producto")
    
    # SEGUIMIENTO
    estado = models.CharField(max_length=20, choices=ESTADOS_RECLAMO, default='INGRESADO')
    fecha_ultima_actualizacion = models.DateField(auto_now=True)
    observaciones_proveedor = models.TextField(blank=True)
    solucion_aplicada = models.TextField(blank=True)
    
    # DATOS DE CONTACTO
    contacto_cliente = models.CharField(max_length=100, blank=True)
    telefono_contacto = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = 'Reclamo de Garantía'
        verbose_name_plural = 'Reclamos de Garantía'
        ordering = ['-fecha_reclamo']
    
    def __str__(self):
        return f"Reclamo {self.numero_reclamo} - {self.producto.producto}"
    
    def generar_numero_reclamo(self):
        from datetime import datetime
        if not self.numero_reclamo:
            fecha = datetime.now().strftime("%Y%m%d")
            ultimo = ReclamoGarantia.objects.filter(
                numero_reclamo__startswith=fecha
            ).count()
            self.numero_reclamo = f"{fecha}-{ultimo + 1:03d}"
    
    def save(self, *args, **kwargs):
        if not self.numero_reclamo:
            self.generar_numero_reclamo()
        super().save(*args, **kwargs)

class Gasto(models.Model):
    rubro = models.ForeignKey(RubroGasto, on_delete=models.PROTECT)
    fecha = models.DateField(default=timezone.now)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    comprobante = models.CharField(max_length=100, blank=True)
    pagado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Gastos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.rubro} - ${self.monto} - {self.fecha}"

class PagoSueldo(models.Model):
    empleado = models.CharField(max_length=200)
    fecha = models.DateField(default=timezone.now)
    periodo = models.CharField(max_length=50, help_text="Ej: Enero 2024")
    sueldo_neto = models.DecimalField(max_digits=10, decimal_places=2)
    aportes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Pago de Sueldo'
        verbose_name_plural = 'Pagos de Sueldos'
    
    def save(self, *args, **kwargs):
        self.total = self.sueldo_neto + self.aportes
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Sueldo {self.empleado} - {self.periodo}"

# MODELOS DE CAJA
class Caja(models.Model):
    ESTADOS = [
        ('ABIERTA', 'Caja Abierta'),
        ('CERRADA', 'Caja Cerrada')
    ]
    
    fecha = models.DateField(default=timezone.now, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='CERRADA')
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    egresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Cajas'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Caja {self.fecha} - ${self.saldo_final}"

class MovimientoCaja(models.Model):
    TIPOS = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso')
    ]
    
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='movimientos')
    fecha_hora = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    comprobante = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - ${self.monto} - {self.concepto}"

class RetiroCaja(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='retiros')
    fecha = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=200)
    destinatario = models.CharField(max_length=200)
    autorizado_por = models.CharField(max_length=200, blank=True)
    comprobante = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Retiro de Caja'
        verbose_name_plural = 'Retiros de Caja'
        ordering = ['-fecha']
    
    def __str__(self):
=======
# models.py - VERSIÓN CORREGIDA
from django.db import models
from django.utils import timezone

class RubroGasto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    tipo = models.CharField(max_length=20, choices=[
        ('FIJO', 'Gasto Fijo'),
        ('VARIABLE', 'Gasto Variable'),
        ('EXTRA', 'Gasto Extraordinario')
    ], default='FIJO')
    
    class Meta:
        verbose_name = 'Rubro de Gasto'
        verbose_name_plural = 'Rubros de Gastos'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class Proveedor(models.Model):
    TIPOS = [
        ('MONOTRIBUTO', 'Monotributista'),
        ('RESPONSABLE', 'Responsable Inscripto'),
        ('EXENTO', 'Exento'),
        ('CONSUMIDOR', 'Consumidor Final')
    ]
    
    nombre = models.CharField(max_length=200)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # DATOS FISCALES
    cuit = models.CharField(max_length=13, blank=True, help_text="Formato: 20-12345678-9")
    tipo_iva = models.CharField(max_length=20, choices=TIPOS, default='RESPONSABLE')
    direccion = models.TextField(blank=True)
    localidad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    # DATOS COMERCIALES
    plazo_garantia = models.PositiveIntegerField(
        default=12, 
        help_text="Meses de garantía por defecto"
    )
    condiciones_garantia = models.TextField(
        blank=True, 
        help_text="Términos y condiciones de la garantía"
    )
    contacto_garantias = models.CharField(max_length=100, blank=True)
    telefono_garantias = models.CharField(max_length=20, blank=True)
    
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True, help_text="Observaciones internas")
    
    class Meta:
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def compras_realizadas(self):
        return self.compramercaderia_set.count()
    
    def total_compras(self):
        from django.db.models import Sum
        result = self.compramercaderia_set.aggregate(total=Sum('total'))
        return result['total'] or 0

class CompraMercaderia(models.Model):
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado')
    ]
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha_compra = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    numero_factura = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR')
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Compra de Mercadería'
        verbose_name_plural = 'Compras de Mercadería'
    
    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor}"

class ItemCompra(models.Model):
    compra = models.ForeignKey(CompraMercaderia, on_delete=models.CASCADE, related_name='items')
    producto = models.CharField(max_length=200)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Item de Compra'
        verbose_name_plural = 'Items de Compra'
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

# ⬇️ CORREGIDO: MODELOS DE GARANTÍA
class ProductoConGarantia(models.Model):
    ESTADOS_GARANTIA = [
        ('VIGENTE', 'Garantía Vigente'),
        ('VENCIDA', 'Garantía Vencida'),
        ('EN_PROCESO', 'En Proceso de Garantía'),
        ('FINALIZADA', 'Garantía Finalizada')
    ]
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    compra = models.ForeignKey(CompraMercaderia, on_delete=models.CASCADE)
    producto = models.CharField(max_length=200)
    modelo = models.CharField(max_length=100, blank=True)
    numero_serie = models.CharField(max_length=100, blank=True)
    
    # DATOS DE GARANTÍA
    fecha_compra = models.DateField(default=timezone.now)  # ⬅️ Agregué default
    fecha_inicio_garantia = models.DateField(default=timezone.now)  # ⬅️ Agregué default
    fecha_fin_garantia = models.DateField(blank=True, null=True)  # ⬅️ Permite null
    meses_garantia = models.PositiveIntegerField(default=12)
    estado_garantia = models.CharField(max_length=20, choices=ESTADOS_GARANTIA, default='VIGENTE')
    
    # INFORMACIÓN ADICIONAL
    numero_factura = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Producto con Garantía'
        verbose_name_plural = 'Productos con Garantía'
    
    def __str__(self):
        return f"{self.producto} - {self.numero_serie or 'Sin serie'}"
    
    def dias_restantes_garantia(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        
        # ⬇️ CORRECCIÓN: Verificar que fecha_fin_garantia no sea None
        if not self.fecha_fin_garantia:
            return "No definida"
        
        if hoy > self.fecha_fin_garantia:
            return 0
        return (self.fecha_fin_garantia - hoy).days
    
    def save(self, *args, **kwargs):
        # ⬇️ CORRECCIÓN: Calcular fecha fin SIEMPRE que haya fecha_inicio
        if self.fecha_inicio_garantia and not self.fecha_fin_garantia:
            from datetime import timedelta
            self.fecha_fin_garantia = self.fecha_inicio_garantia + timedelta(days=self.meses_garantia * 30)
        
        # ⬇️ CORRECCIÓN: Solo actualizar estado si fecha_fin existe
        if self.fecha_fin_garantia:
            from django.utils import timezone
            hoy = timezone.now().date()
            if hoy > self.fecha_fin_garantia:
                self.estado_garantia = 'VENCIDA'
            elif self.estado_garantia == 'VENCIDA' and hoy <= self.fecha_fin_garantia:
                self.estado_garantia = 'VIGENTE'
            
        super().save(*args, **kwargs)

class ReclamoGarantia(models.Model):
    ESTADOS_RECLAMO = [
        ('INGRESADO', 'Reclamo Ingresado'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADO', 'Garantía Aprobada'),
        ('RECHAZADO', 'Garantía Rechazada'),
        ('REPARADO', 'Producto Reparado'),
        ('REEMPLAZADO', 'Producto Reemplazado'),
        ('FINALIZADO', 'Reclamo Finalizado')
    ]
    
    producto = models.ForeignKey(ProductoConGarantia, on_delete=models.CASCADE)
    fecha_reclamo = models.DateField(default=timezone.now)
    numero_reclamo = models.CharField(max_length=50, blank=True)  # ⬅️ Cambié unique=True por blank=True
    
    # DATOS DEL RECLAMO
    descripcion_problema = models.TextField()
    sintomas = models.TextField(blank=True, help_text="Qué falla presenta el producto")
    accesorios_entregados = models.TextField(blank=True, help_text="Accesorios que se entregaron con el producto")
    
    # SEGUIMIENTO
    estado = models.CharField(max_length=20, choices=ESTADOS_RECLAMO, default='INGRESADO')
    fecha_ultima_actualizacion = models.DateField(auto_now=True)
    observaciones_proveedor = models.TextField(blank=True)
    solucion_aplicada = models.TextField(blank=True)
    
    # DATOS DE CONTACTO
    contacto_cliente = models.CharField(max_length=100, blank=True)
    telefono_contacto = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = 'Reclamo de Garantía'
        verbose_name_plural = 'Reclamos de Garantía'
        ordering = ['-fecha_reclamo']
    
    def __str__(self):
        return f"Reclamo {self.numero_reclamo} - {self.producto.producto}"
    
    def generar_numero_reclamo(self):
        from datetime import datetime
        if not self.numero_reclamo:
            fecha = datetime.now().strftime("%Y%m%d")
            ultimo = ReclamoGarantia.objects.filter(
                numero_reclamo__startswith=fecha
            ).count()
            self.numero_reclamo = f"{fecha}-{ultimo + 1:03d}"
    
    def save(self, *args, **kwargs):
        if not self.numero_reclamo:
            self.generar_numero_reclamo()
        super().save(*args, **kwargs)

class Gasto(models.Model):
    rubro = models.ForeignKey(RubroGasto, on_delete=models.PROTECT)
    fecha = models.DateField(default=timezone.now)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    comprobante = models.CharField(max_length=100, blank=True)
    pagado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Gastos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.rubro} - ${self.monto} - {self.fecha}"

class PagoSueldo(models.Model):
    empleado = models.CharField(max_length=200)
    fecha = models.DateField(default=timezone.now)
    periodo = models.CharField(max_length=50, help_text="Ej: Enero 2024")
    sueldo_neto = models.DecimalField(max_digits=10, decimal_places=2)
    aportes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Pago de Sueldo'
        verbose_name_plural = 'Pagos de Sueldos'
    
    def save(self, *args, **kwargs):
        self.total = self.sueldo_neto + self.aportes
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Sueldo {self.empleado} - {self.periodo}"

# MODELOS DE CAJA
class Caja(models.Model):
    ESTADOS = [
        ('ABIERTA', 'Caja Abierta'),
        ('CERRADA', 'Caja Cerrada')
    ]
    
    fecha = models.DateField(default=timezone.now, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='CERRADA')
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    egresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Cajas'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Caja {self.fecha} - ${self.saldo_final}"

class MovimientoCaja(models.Model):
    TIPOS = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso')
    ]
    
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='movimientos')
    fecha_hora = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    comprobante = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - ${self.monto} - {self.concepto}"

class RetiroCaja(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='retiros')
    fecha = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    concepto = models.CharField(max_length=200)
    destinatario = models.CharField(max_length=200)
    autorizado_por = models.CharField(max_length=200, blank=True)
    comprobante = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Retiro de Caja'
        verbose_name_plural = 'Retiros de Caja'
        ordering = ['-fecha']
    
    def __str__(self):
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
        return f"Retiro {self.destinatario} - ${self.monto}"