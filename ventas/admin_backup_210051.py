from django.contrib import admin
from .models import Venta, DetalleVenta

# 🔥 CORREGIDO: Quitar autocomplete_fields problemático
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    # ❌ REMOVER autocomplete_fields que causa problemas
    # autocomplete_fields = ['producto']  # Comentado porque causa errores
    
    # Campos básicos que SÍ funcionan
    fields = ['producto', 'cantidad', 'precio_unitario']
    readonly_fields = ['precio_unitario']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    inlines = [DetalleVentaInline]
    list_display = ['id', 'fecha', 'cliente', 'total']
    list_filter = ['fecha']
    search_fields = ['cliente__nombre']  # Solo si existe cliente__nombre
    
    # Campos para el formulario
    fields = ['cliente', 'fecha', 'total']
    readonly_fields = ['total']