import random
import string
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.utils import timezone
import requests
import uuid
from urllib.parse import quote

# --- Modelos INDEPENDIENTES (van primero) ---
class CotizacionDolar(models.Model):
    valor_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_venta = models.DecimalField(max_digits=10, decimal_places=2, default=1400.00)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fuente = models.CharField(max_length=100, default='Manual')
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cotización del Dólar"
        verbose_name_plural = "Cotizaciones del Dólar"
        ordering = ['-fecha_actualizacion']

    def __str__(self):
        return f"Dólar: Compra ${self.valor_compra} - Venta ${self.valor_venta}"

    def save(self, *args, **kwargs):
        if self.activo:
            CotizacionDolar.objects.filter(activo=True).update(activo=False)
        super().save(*args, **kwargs)

    @classmethod
    def obtener_cotizacion_actual(cls):
        cotizacion = cls.objects.filter(activo=True).first()
        if not cotizacion:
            cotizacion = cls(valor_compra=1300.00, valor_venta=1400.00, activo=True)
            cotizacion.save()
        return cotizacion

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    categoria_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategorias')
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"
        ordering = ['nombre']
    
    def __str__(self):
        if self.categoria_padre:
            return f"{self.categoria_padre.nombre} > {self.nombre}"
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            counter = 1
            while CategoriaProducto.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

# --- Modelo PRINCIPAL Producto ---
class Producto(models.Model):
    def generar_codigo_barras():
        while True:
            codigo = ''.join(random.choices(string.digits, k=12))
            suma = sum(int(codigo[i]) * (3 if i % 2 != 0 else 1) for i in range(12))
            digito_verificador = (10 - (suma % 10)) % 10
            codigo_completo = codigo + str(digito_verificador)
            if not Producto.objects.filter(codigo_barras=codigo_completo).exists():
                return codigo_completo

    nombre = models.CharField(max_length=200, verbose_name="Nombre del producto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    codigo_barras = models.CharField(max_length=13, unique=True, default=generar_codigo_barras, verbose_name="Código de Barras")
    precio_compra_usd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Compra (USD)")
    precio_venta_usd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Venta (USD)")
    stock_actual = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")
    stock_minimo = models.PositiveIntegerField(default=5, verbose_name="Stock Mínimo")
    activo = models.BooleanField(default=True, verbose_name="¿Está activo?")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    imagen_principal = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen Principal")
    descripcion_larga = models.TextField(blank=True, verbose_name="Descripción Larga (Web)")
    caracteristicas = models.JSONField(default=dict, blank=True, verbose_name="Características Técnicas")
    slug = models.SlugField(unique=True, blank=True)
    meta_titulo = models.CharField(max_length=60, blank=True)
    meta_descripcion = models.CharField(max_length=160, blank=True)
    publicado_web = models.BooleanField(default=False, verbose_name="Publicado en Web")
    tiene_garantia = models.BooleanField(default=False, verbose_name="Tiene Garantía")
    meses_garantia = models.PositiveIntegerField(default=0, verbose_name="Meses de Garantía")
    condiciones_garantia = models.TextField(blank=True, verbose_name="Condiciones de Garantía")
    proveedor_garantia = models.CharField(max_length=100, blank=True, verbose_name="Proveedor/Garantía")
    tags = models.CharField(max_length=200, blank=True, help_text="Separar con comas")
    orden_destacado = models.IntegerField(default=0, verbose_name="Orden en Destacados")
    sku = models.CharField(max_length=50, blank=True, null=True, unique=True, verbose_name="SKU")
    
    # 🆕 CAMPO NUEVO AGREGADO
    usar_factor_dolar = models.BooleanField(default=False, verbose_name="Usar factor dólar")
    
    # ✏️ CAMPO EXISTENTE MODIFICADO (default=30)
    margen_ganancia = models.DecimalField(
        max_digits=5, decimal_places=2, default=30, 
        verbose_name="Margen de Ganancia (%)"
    )
    
    destacado = models.BooleanField(default=False, verbose_name="Producto Destacado")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # --- Lógica de Slug, Código de Barras y SKU ---
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            counter = 1
            while Producto.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        if not self.codigo_barras:
            # ✅ CORRECCIÓN 2: Llamar a la función a través de la Clase
            self.codigo_barras = Producto.generar_codigo_barras()
        
        if not self.sku:
            base_sku = slugify(self.nombre).upper()[:20]
            sku = base_sku
            counter = 1
            while Producto.objects.filter(sku=sku).exists():
                sku = f"{base_sku}-{counter}"
                counter += 1
            self.sku = sku
        
        # ♻️ LÓGICA DE PRECIOS MEJORADA (FUSIONADA)
        if self.usar_factor_dolar and self.precio_compra_usd > 0:
            # MODO AUTOMÁTICO: Calcular Precio Venta (USD) desde el Margen
            margen_decimal = 1 + (self.margen_ganancia / 100)
            self.precio_venta_usd = round(self.precio_compra_usd * margen_decimal, 2)
        
        elif not self.usar_factor_dolar and self.precio_compra_usd > 0 and self.precio_venta_usd > 0:
            # MODO MANUAL: Calcular Margen desde los Precios
            # (Solo si no es automático, para no sobrescribir el margen del usuario)
            self.margen_ganancia = round(((self.precio_venta_usd - self.precio_compra_usd) / self.precio_compra_usd) * 100, 2)
        
        elif not self.usar_factor_dolar and self.precio_compra_usd > 0 and self.precio_venta_usd == 0:
            # MODO MANUAL (Fallback): Si solo hay costo, usar margen por defecto (ej. 30%)
            margen_decimal = 1 + (self.margen_ganancia / 100)
            self.precio_venta_usd = round(self.precio_compra_usd * margen_decimal, 2)

        super().save(*args, **kwargs)

    @property
    def precio_venta_ars(self):
        try:
            cotizacion = CotizacionDolar.obtener_cotizacion_actual()
            return round(self.precio_venta_usd * cotizacion.valor_venta, 2)
        except:
            return 0

    @property
    def precio_compra_ars(self):
        try:
            cotizacion = CotizacionDolar.obtener_cotizacion_actual()
            return round(self.precio_compra_usd * cotizacion.valor_compra, 2)
        except:
            return 0

    @property
    def imagen_destacada(self):
        if self.imagen_principal:
            return self.imagen_principal
        primera_imagen = self.imagenes_galeria.first()
        if primera_imagen:
            return primera_imagen.imagen
        return None

# --- Modelos DEPENDIENTES de Producto (van después) ---
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes_galeria')
    imagen = models.ImageField(upload_to='productos/galeria/')
    orden = models.IntegerField(default=0)
    titulo = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['orden']
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"
    
    def __str__(self):
        return self.titulo or f"Imagen {self.id}"

# --- Otros modelos ---
class ClaseEquipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Clase de Equipo")
    
    def __str__(self): 
        return self.nombre
    
    class Meta:
        verbose_name = "Clase de Equipo"
        verbose_name_plural = "Clases de Equipos"
        ordering = ['nombre']

class MarcaEquipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Marca")
    
    def __str__(self): 
        return self.nombre
    
    class Meta:
        verbose_name = "Marca de Equipo"
        verbose_name_plural = "Marcas de Equipos"
        ordering = ['nombre']

class ModeloEquipo(models.Model):
    clase = models.ForeignKey(ClaseEquipo, on_delete=models.PROTECT, verbose_name="Clase de Equipo", null=True, blank=True)
    marca = models.ForeignKey(MarcaEquipo, on_delete=models.CASCADE, verbose_name="Marca")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Modelo")
    
    # ✅ CORRECCIÓN 1: Cambiar "Déf" y agregar "__str__"
    def __str__(self):
        if self.clase: 
            return f"{self.clase} {self.marca} {self.nombre}"
        return f"{self.marca} {self.nombre}"
    
    class Meta:
        verbose_name = "Modelo de Equipo"
        verbose_name_plural = "Modelos de Equipos"
        ordering = ['clase', 'marca', 'nombre']