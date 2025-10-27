# admin.py - VERSIÓN CORREGIDA CON IMPORTACIONES
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from django.contrib import messages
from django.http import HttpResponse
from .models import (
    RubroGasto, Proveedor, CompraMercaderia, ItemCompra, 
    Gasto, PagoSueldo, ProductoConGarantia, ReclamoGarantia,
    Caja, MovimientoCaja, RetiroCaja
)
import tempfile
import os

# 🎯 ADMIN ESPECIALIZADO PARA FINANZAS
def crear_admin_finanzas(model):
    class ModelAdminFinanzas(admin.ModelAdmin):
        def get_list_display(self, request):
            campos_base = ['__str__']
            
            nombres_campos = [f.name for f in model._meta.fields]
            
            # Campos financieros
            for campo_fin in ['monto', 'total', 'subtotal', 'saldo_final', 'sueldo_neto']:
                if campo_fin in nombres_campos:
                    campos_base.append(campo_fin)
                    break
            
            # Campos de fecha
            for campo_fecha in ['fecha', 'fecha_compra', 'fecha_pago', 'fecha_reclamo']:
                if campo_fecha in nombres_campos:
                    campos_base.append(campo_fecha)
                    break
            
            # Campos de estado
            for campo_estado in ['estado', 'activo', 'pagado', 'estado_garantia']:
                if campo_estado in nombres_campos:
                    campos_base.append('estado_coloreado')
                    break
            
            return campos_base
        
        def estado_coloreado(self, obj):
            valor = getattr(obj, 'estado', None) or getattr(obj, 'pagado', None) or getattr(obj, 'activo', None) or getattr(obj, 'estado_garantia', None)
            
            if valor in [True, 'pagado', 'PAGADO', 'activo', 'ABIERTA', 'VIGENTE', 'APROBADO', 'FINALIZADO']:
                return format_html('<span style="color: green;">✅ {}</span>', 'Activo' if valor is True else str(valor).title())
            elif valor in [False, 'pendiente', 'PENDIENTE', 'inactivo', 'CERRADA', 'VENCIDA', 'RECHAZADO']:
                return format_html('<span style="color: red;">❌ {}</span>', 'Inactivo' if valor is False else str(valor).title())
            elif valor in ['EN_PROCESO', 'EN_REVISION']:
                return format_html('<span style="color: orange;">⚠️ {}</span>', str(valor).title())
            else:
                return str(valor)
        estado_coloreado.short_description = 'Estado'
        
        def get_list_filter(self, request):
            filtros = []
            for field in model._meta.fields:
                if field.name in ['fecha', 'estado', 'pagado', 'activo', 'tipo', 'estado_garantia']:
                    filtros.append(field.name)
                if len(filtros) >= 3:
                    break
            return filtros
        
        def get_search_fields(self, request):
            return [f.name for f in model._meta.fields if f.get_internal_type() in ['CharField', 'TextField']][:2]
    
    return ModelAdminFinanzas

# 📦 ADMIN PERSONALIZADO PARA COMPRAS CON ACCIÓN DE GARANTÍAS
@admin.register(CompraMercaderia)
class CompraMercaderiaAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 
        'proveedor', 
        'fecha_compra', 
        'total', 
        'estado_coloreado',
        'productos_garantia_generados'
    ]
    list_filter = ['estado', 'pagado', 'fecha_compra', 'proveedor']
    search_fields = ['numero_factura', 'descripcion', 'proveedor__nombre']
    actions = ['generar_productos_garantia', 'marcar_como_pagado']
    
    def estado_coloreado(self, obj):
        colors = {
            'PAGADO': 'green',
            'PENDIENTE': 'orange',
            'BORRADOR': 'gray',
            'CANCELADO': 'red'
        }
        color = colors.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    
    def productos_garantia_generados(self, obj):
        count = ProductoConGarantia.objects.filter(compra=obj).count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'red',
            f"{count} productos"
        )
    productos_garantia_generados.short_description = 'Garantías'
    
    def generar_productos_garantia(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "❌ Seleccioná SOLO UNA compra", messages.ERROR)
            return
        
        compra = queryset.first()
        
        # Verificar que tenga items
        if not compra.items.exists():
            self.message_user(request, "❌ Esta compra no tiene items", messages.ERROR)
            return
        
        productos_creados = 0
        
        for item in compra.items.all():
            # Crear producto con garantía por cada item
            for i in range(int(item.cantidad)):
                producto_garantia = ProductoConGarantia(
                    proveedor=compra.proveedor,
                    compra=compra,
                    producto=item.producto,
                    fecha_compra=compra.fecha_compra,
                    fecha_inicio_garantia=compra.fecha_compra,
                    meses_garantia=compra.proveedor.plazo_garantia,
                    numero_factura=compra.numero_factura,
                    modelo=f"{item.producto} - Lote {compra.id}"
                )
                producto_garantia.save()
                productos_creados += 1
        
        self.message_user(
            request, 
            f"✅ {productos_creados} productos con garantía creados para la compra #{compra.id}",
            messages.SUCCESS
        )
    
    generar_productos_garantia.short_description = "🛡️ Generar productos con garantía"
    
    def marcar_como_pagado(self, request, queryset):
        updated = queryset.update(estado='PAGADO', pagado=True)
        self.message_user(request, f"✅ {updated} compras marcadas como pagadas", messages.SUCCESS)
    
    marcar_como_pagado.short_description = "💰 Marcar como pagado"

# 🛡️ ADMIN PARA PRODUCTOS CON GARANTÍA
@admin.register(ProductoConGarantia)
class ProductoConGarantiaAdmin(admin.ModelAdmin):
    list_display = [
        'producto',
        'numero_serie',
        'proveedor',
        'fecha_compra',
        'fecha_fin_garantia',
        'dias_restantes_garantia_coloreado',
        'estado_garantia_coloreado'
    ]
    list_filter = ['proveedor', 'estado_garantia', 'fecha_compra']
    search_fields = ['producto', 'numero_serie', 'modelo', 'numero_factura']
    readonly_fields = ['dias_restantes_garantia']
    actions = ['generar_certificados_masivos']
    
    # NUEVO MÉTODO CORREGIDO
    def dias_restantes_garantia_coloreado(self, obj):
        dias = obj.dias_restantes_garantia()
        
        if dias == "No definida":
            return format_html('<span style="color: gray;">─</span>')
        elif dias <= 0: # Corregido para manejar 0 y valores negativos
            return format_html('<span style="color: red; font-weight: bold;">VENCIDA</span>')
        elif dias <= 30:
            return format_html('<span style="color: orange; font-weight: bold;">{} días</span>', dias)
        else:
            return format_html('<span style="color: green;">{} días</span>', dias)
    dias_restantes_garantia_coloreado.short_description = 'Días Restantes'
    
    def estado_garantia_coloreado(self, obj):
        colors = {
            'VIGENTE': 'green',
            'VENCIDA': 'red', 
            'EN_PROCESO': 'orange',
            'FINALIZADA': 'gray'
        }
        color = colors.get(obj.estado_garantia, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_garantia_display()
        )
    estado_garantia_coloreado.short_description = 'Estado Garantía'

# 🔧 ADMIN PARA RECLAMOS DE GARANTÍA
@admin.register(ReclamoGarantia)
class ReclamoGarantiaAdmin(admin.ModelAdmin):
    list_display = [
        'numero_reclamo',
        'producto',
        'fecha_reclamo',
        'estado_coloreado',
        'contacto_cliente',
        'dias_desde_reclamo'
    ]
    list_filter = ['estado', 'fecha_reclamo']
    search_fields = ['numero_reclamo', 'producto__producto', 'contacto_cliente']
    readonly_fields = ['fecha_ultima_actualizacion', 'numero_reclamo']
    actions = ['marcar_como_aprobado', 'marcar_como_finalizado']
    
    def estado_coloreado(self, obj):
        colors = {
            'INGRESADO': 'blue',
            'EN_REVISION': 'orange',
            'APROBADO': 'green',
            'RECHAZADO': 'red',
            'REPARADO': 'purple',
            'REEMPLAZADO': 'teal',
            'FINALIZADO': 'gray'
        }
        color = colors.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_coloreado.short_description = 'Estado'
    
    def dias_desde_reclamo(self, obj):
        from django.utils import timezone
        dias = (timezone.now().date() - obj.fecha_reclamo).days
        return f"{dias} días"
    dias_desde_reclamo.short_description = 'Días'
    
    def marcar_como_aprobado(self, request, queryset):
        updated = queryset.update(estado='APROBADO')
        self.message_user(request, f"✅ {updated} reclamos marcados como aprobados", messages.SUCCESS)
    
    marcar_como_aprobado.short_description = "✅ Marcar como aprobado"
    
    def marcar_como_finalizado(self, request, queryset):
        updated = queryset.update(estado='FINALIZADO')
        self.message_user(request, f"✅ {updated} reclamos marcados como finalizados", messages.SUCCESS)
    
    marcar_como_finalizado.short_description = "🏁 Marcar como finalizado"

# 📊 ADMIN PARA PROVEEDORES MEJORADO
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'cuit', 
        'tipo_iva',
        'telefono',
        'plazo_garantia',
        'compras_realizadas',
        'total_compras',
        'activo'
    ]
    list_filter = ['tipo_iva', 'activo', 'plazo_garantia']
    search_fields = ['nombre', 'cuit', 'contacto']
    list_editable = ['activo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'contacto', 'telefono', 'email', 'activo')
        }),
        ('Datos Fiscales', {
            'fields': ('cuit', 'tipo_iva', 'direccion', 'localidad', 'codigo_postal')
        }),
        ('Políticas de Garantía', {
            'fields': ('plazo_garantia', 'condiciones_garantia', 'contacto_garantias', 'telefono_garantias')
        }),
        ('Observaciones', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )

# 📋 REGISTRO AUTOMÁTICO PARA EL RESTO DE MODELOS
from django.apps import apps

app_config = apps.get_app_config('finanzas')
modelos_personalizados = ['Proveedor', 'CompraMercaderia', 'ProductoConGarantia', 'ReclamoGarantia']
modelos_registrados = []

for model in app_config.get_models():
    if model.__name__ not in modelos_personalizados:
        try:
            admin.site.register(model, crear_admin_finanzas(model))
            modelos_registrados.append(model.__name__)
            print(f"✅ Registrado: {model._meta.verbose_name}")
        except:
            pass

print(f"🎯 Modelos con admin personalizado: {modelos_personalizados}")