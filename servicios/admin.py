from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from urllib.parse import quote
from django.utils import timezone
from configuracion.models import Empresa as ConfiguracionNegocio
from .models import OrdenTaller, ItemReparacion

# =============================================================================
# ADMIN CORREGIDO - WHATSAPP FUNCIONANDO
# =============================================================================

# 1. DESREGISTRAR MODELOS POR DEFECTO
admin.site.unregister(Group)
admin.site.unregister(User)

# 2. ADMIN PARA CONFIGURACIÓN DEL NEGOCIO
@admin.register(ConfiguracionNegocio)
class ConfiguracionNegocioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email']
    fieldsets = [
        ('🏗️ INFORMACIÓN DEL NEGOCIO', {
            'fields': [
                'nombre',
                ('telefono', 'email'),
                'direccion',
                'logo'
            ]
        }),
        ('📱 CONFIGURACIÓN WHATSAPP', {
            'fields': ['mensaje_whatsapp']
        })
    ]
    
    def has_add_permission(self, request):
        return not ConfiguracionNegocio.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

# 3. INLINE PARA ITEMS DE REPARACIÓN
class ItemReparacionInline(admin.TabularInline):
    model = ItemReparacion
    extra = 1
    autocomplete_fields = ['producto']

# 4. ADMIN PRINCIPAL COMPLETO - WHATSAPP FUNCIONANDO
@admin.register(OrdenTaller)
class OrdenTallerAdmin(admin.ModelAdmin):
    list_display = ['numero_orden', 'cliente', 'equipo', 'estado_color', 'fecha_ingreso', 'acciones_rapidas']
    list_filter = ['estado', 'prioridad', 'fecha_ingreso']
    search_fields = ['cliente__nombre', 'equipo', 'numero_serie']
    list_per_page = 20
    readonly_fields = ['url_whatsapp_display']
    
    inlines = [ItemReparacionInline]
    
    fieldsets = [
        ('👤 INFORMACIÓN DEL CLIENTE', {
            'fields': ['cliente']
        }),
        ('🔧 INFORMACIÓN DEL EQUIPO', {
            'fields': [
                'equipo',
                'numero_serie',
                'problema',
                'accesorios'
            ]
        }),
        ('⚙️ DIAGNÓSTICO Y REPARACIÓN', {
            'fields': ['diagnostico', 'solucion', 'observaciones']
        }),
        ('📊 ESTADO Y SEGUIMIENTO', {
            'fields': [
                ('estado', 'prioridad'),
                ('fecha_ingreso', 'fecha_prometida')
            ]
        }),
        ('💰 INFORMACIÓN ECONÓMICA', {
            'fields': [
                ('presupuesto', 'costo_final'),
                'seña'
            ]
        }),
        ('🔗 CONSULTAS WHATSAPP', {
            'fields': ['url_whatsapp_display'],
            'classes': ['collapse']
        })
    ]
    
    def estado_color(self, obj):
        """Muestra el estado con colores ÚNICOS"""
        colors = {
            'recibido': '🔵',      # Azul
            'diagnostico': '🟡',   # Amarillo  
            'presupuesto': '🟠',   # Naranja
            'espera_repuesto': '🟣', # Violeta
            'reparacion': '🔴',    # Rojo
            'completado': '🟢',    # Verde
            'entregado': '📦',     # Paquete
            'cancelado': '⚫',     # Negro
        }
        
        color = colors.get(obj.estado, '⚪')
        return format_html(
            '{} {}',
            color, obj.get_estado_display()
        )
    estado_color.short_description = 'Estado'

    def url_whatsapp_display(self, obj):
        if hasattr(obj, 'codigo_consulta') and obj.codigo_consulta:
            return format_html(
                '<a href="{}" target="_blank" style="background: #25D366; color: white; padding: 10px 15px; border-radius: 5px; text-decoration: none; display: inline-block;">📱 Enviar Link de Consulta al Cliente</a>',
                obj.url_consulta_whatsapp
            )
        return "Guardar la orden para generar el código"
    url_whatsapp_display.short_description = 'Link WhatsApp'
    
    def acciones_rapidas(self, obj):
        """Botones de acción en la lista"""
        return format_html(
            '''
            <div style="display: flex; gap: 3px; flex-wrap: nowrap;">
                <a href="/admin/servicios/ordentaller/{}/whatsapp/" 
                   style="background: #25D366; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 12px; white-space: nowrap;"
                   title="Enviar WhatsApp de reparación completada">
                    📱 Reparada
                </a>
            </div>
            ''',
            obj.id
        )
    acciones_rapidas.short_description = 'Acción Rápida'
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_buttons'] = True
        
        config = ConfiguracionNegocio.objects.first()
        extra_context['config'] = config
        
        orden = get_object_or_404(OrdenTaller, id=object_id)
        
        extra_context['botones'] = [
            {
                'nombre': '🖨️ IMPRIMIR ORDEN',
                'url': f'/admin/servicios/ordentaller/{object_id}/imprimir/',
                'clase': 'default',
                'target': '_blank'
            },
            {
                'nombre': '📧 ENVIAR EMAIL', 
                'url': f'/admin/servicios/ordentaller/{object_id}/email/',
                'clase': 'default'
            },
            {
                'nombre': '📱 AVISAR REPARACIÓN COMPLETADA',
                'url': f'/admin/servicios/ordentaller/{object_id}/whatsapp/', 
                'clase': 'success'
            }
        ]
        
        if hasattr(orden, 'codigo_consulta') and orden.codigo_consulta:
            extra_context['botones'].append({
                'nombre': '🔗 LINK CONSULTA WHATSAPP',
                'url': orden.url_consulta_whatsapp,
                'clase': 'info',
                'target': '_blank'
            })
        
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        
        custom_urls = [
            path('<path:object_id>/imprimir/', self.imprimir_orden, name='orden_imprimir'),
            path('<path:object_id>/email/', self.enviar_email, name='orden_email'),
            path('<path:object_id>/whatsapp/', self.enviar_whatsapp_reparacion_completada, name='orden_whatsapp'),
        ]
        
        return custom_urls + urls
    
    def _get_orden_id(self, object_id):
        if '/' in object_id:
            return object_id.split('/')[0]
        return object_id
    
    def enviar_whatsapp_reparacion_completada(self, request, object_id):
        """✅ WHATSAPP QUE SÍ FUNCIONA - Reparación completada"""
        orden_id = self._get_orden_id(object_id)
        orden = get_object_or_404(OrdenTaller, id=orden_id)
        config = ConfiguracionNegocio.objects.first()
        
        # ✅ MARCAR COMO COMPLETADO AUTOMÁTICAMENTE
        if orden.estado != 'completado':
            orden.estado = 'completado'
            orden.save()
            messages.success(request, f'✅ Orden {orden.numero_orden} marcada como COMPLETADA')
        
        # Calcular costos
        costo_repuestos = sum(item.subtotal for item in orden.repuestos_usados.all())
        costo_total = orden.costo_final + costo_repuestos
        
        # ✅ MENSAJE CLARO Y DIRECTO - CORREGIDO SIN F-STRING PROBLEMÁTICOS
        mensaje_lines = [
            f"¡Hola {orden.cliente.nombre}!",
            "",
            "🎉 *¡BUENAS NOTICIAS!*",
            "",
            f"Tu equipo *{orden.equipo}* ya está *REPARADO Y LISTO* para retirar.",
            "",
            "📋 *Detalles de la reparación:*",
            f"• Orden: {orden.numero_orden}",
            f"• Equipo: {orden.equipo}",
            f"• Problema: {orden.problema}",
            f"• Solución: {orden.solucion or 'Reparación técnica completada'}",
            ""
        ]

        # Agregar repuestos si existen
        if orden.repuestos_usados.exists():
            mensaje_lines.append("• Repuestos utilizados:")
            for item in orden.repuestos_usados.all():
                mensaje_lines.append(f"   - {item.producto.nombre} (x{item.cantidad})")
            mensaje_lines.append("")

        # Información económica
        mensaje_lines.extend([
            "💰 *Información de pago:*",
            f"• Total: *${costo_total:.2f}*",
            f"• Seña: ${orden.seña}",
            f"• Saldo: *${costo_total - orden.seña:.2f}*",
            "",
            "⏰ *Horario de retiro:*",
            "Lunes a Viernes: 8:00 a 18:00",
            "Sábados: 8:00 a 13:00",
            "",
            f"📍 *Dirección:*",
            f"{config.direccion if config else 'Nuestra sucursal'}",
            "",
            f"📞 *Contacto:*",
            f"{config.telefono if config else 'Tu taller de confianza'}",
            "",
            "¡Te esperamos! 😊",
            "",
            f"{config.nombre if config else 'Taller Técnico'}"
        ])

        mensaje = "\n".join(mensaje_lines)
        
        # Limpiar teléfono
        telefono_limpio = ''.join(c for c in orden.cliente.telefono if c.isdigit())
        
        # ✅ REDIRECCIÓN DIRECTA A WHATSAPP - ESTO SÍ FUNCIONA
        url_whatsapp = f'https://web.whatsapp.com/send?phone={telefono_limpio}&text={quote(mensaje)}'
        
        # Mensaje informativo
        messages.info(request, f'📱 Redirigiendo a WhatsApp...')
        messages.info(request, f'👤 Cliente: {orden.cliente.nombre}')
        messages.info(request, f'📞 Teléfono: {orden.cliente.telefono}')
        messages.info(request, f'🔧 Equipo: {orden.equipo}')
        messages.info(request, f'💰 Total: ${costo_total:.2f}')
        
        # ✅ REDIRECCIÓN REAL A WHATSAPP WEB
        return redirect(url_whatsapp)

    def imprimir_orden(self, request, object_id):
        orden_id = self._get_orden_id(object_id)
        orden = get_object_or_404(OrdenTaller, id=orden_id)
        config = ConfiguracionNegocio.objects.first()
        
        costo_productos = sum(item.subtotal for item in orden.repuestos_usados.all())
        costo_total = orden.costo_final + costo_productos
        
        logo_html = f'<img src="/media/{config.logo}" style="max-height: 80px; margin-bottom: 10px;" alt="{config.nombre}">' if config and config.logo else f'<h1>🏗️ {config.nombre if config else "TALLER TÉCNICO"}</h1>'
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Orden #{orden.numero_orden}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .header {{ text-align: center; border-bottom: 3px solid #333; padding-bottom: 15px; margin-bottom: 20px; }}
                .negocio-info {{ text-align: center; margin-bottom: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .section h3 {{ background: #f8f9fa; padding: 10px; margin: -15px -15px 15px -15px; border-bottom: 1px solid #ddd; }}
                .row {{ display: flex; justify-content: space-between; margin: 8px 0; }}
                .label {{ font-weight: bold; min-width: 150px; }}
                .valor {{ flex: 1; }}
                .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 10px; }}
                .producto {{ border-left: 4px solid #3498db; padding-left: 10px; margin: 5px 0; }}
                @media print {{
                    body {{ margin: 0; }}
                    .no-print {{ display: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                {logo_html}
                <h2>ORDEN DE REPARACIÓN N° {orden.numero_orden}</h2>
                <p><strong>Fecha de ingreso:</strong> {orden.fecha_ingreso.strftime("%d/%m/%Y %H:%M")}</p>
            </div>
            
            {f'<div class="negocio-info"><p><strong>{config.nombre}</strong><br>{config.direccion}<br>📞 {config.telefono} | 📧 {config.email}</p></div>' if config else ''}
            
            <div class="section">
                <h3>👤 INFORMACIÓN DEL CLIENTE</h3>
                <div class="row">
                    <span class="label">Nombre:</span>
                    <span class="valor">{orden.cliente.nombre}</span>
                </div>
                <div class="row">
                    <span class="label">Teléfono:</span>
                    <span class="valor">{orden.cliente.telefono}</span>
                </div>
            </div>
            
            <div class="section">
                <h3>🔧 INFORMACIÓN DEL EQUIPO</h3>
                <div class="row">
                    <span class="label">Equipo:</span>
                    <span class="valor">{orden.equipo}</span>
                </div>
                <div class="row">
                    <span class="label">Problema:</span>
                    <span class="valor">{orden.problema}</span>
                </div>
            </div>
            
            <div class="section">
                <h3>⚙️ REPARACIÓN</h3>
                <div class="row">
                    <span class="label">Estado:</span>
                    <span class="valor">{orden.get_estado_display()}</span>
                </div>
                <div class="row">
                    <span class="label">Solución:</span>
                    <span class="valor">{orden.solucion or "Completada"}</span>
                </div>
            </div>
            
            <div class="section">
                <h3>💰 INFORMACIÓN ECONÓMICA</h3>
                <div class="row">
                    <span class="label">Total:</span>
                    <span class="valor"><strong>${costo_total:.2f}</strong></span>
                </div>
            </div>
            
            <div class="footer">
                <p>Documento generado el {timezone.now().strftime("%d/%m/%Y a las %H:%M")}</p>
            </div>
            
            <div class="no-print" style="margin-top: 20px; text-align: center;">
                <button onclick="window.print()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    🖨️ Imprimir
                </button>
            </div>
        </body>
        </html>
        '''
        
        response = HttpResponse(html)
        response['Content-Disposition'] = f'filename="orden_{orden.numero_orden}.html"'
        return response
    
    def enviar_email(self, request, object_id):
        orden_id = self._get_orden_id(object_id)
        orden = get_object_or_404(OrdenTaller, id=orden_id)
        
        costo_repuestos = sum(item.subtotal for item in orden.repuestos_usados.all())
        costo_total = orden.costo_final + costo_repuestos
        
        messages.success(request, f'📧 Email listo para {orden.numero_orden}')
        messages.info(request, f'👤 Cliente: {orden.cliente.nombre}')
        messages.info(request, f'💰 Total: ${costo_total:.2f}')
        messages.warning(request, 'Configure SMTP en settings.py para enviar emails reales')
        
        return redirect('..')

# 5. REGISTRAR ITEMS DE REPARACIÓN
@admin.register(ItemReparacion)
class ItemReparacionAdmin(admin.ModelAdmin):
    list_display = ['orden', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['orden__estado']
    autocomplete_fields = ['producto']

# 6. REGISTRAR USUARIOS
@admin.register(User)
class UserAdminPersonalizado(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']

@admin.register(Group)
class GroupAdminPersonalizado(GroupAdmin):
    list_display = ['name', 'get_user_count']