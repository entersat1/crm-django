from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # 🔥 IMPORTANTE: Usar SOLO campos que existen
    list_display = ['id', 'nombre', 'email', 'telefono']  # Campos básicos que SÍ existen
    
    # Búsqueda en campos que existen
    search_fields = ['nombre', 'email', 'telefono']
    
    # ✅ EL SECRETO: No usar fieldsets complicados, dejar que Django maneje los campos automáticamente
    # Esto evita errores de campos que no existen
    
    # ✅ BOTONES DE ACCIÓN: Tanto "Cambiar" (Editar) como "Eliminar"
    # Por defecto Django ya muestra ambos, pero nos aseguramos:
    
    def get_list_display_links(self, request, list_display):
        '''Hacer que el nombre sea clickeable para editar'''
        return ['nombre']  # Click en nombre para editar
    
    # ✅ PERMISOS COMPLETOS para editar
    def has_change_permission(self, request, obj=None):
        return True  # ✅ Permiso para EDITAR
    
    def has_delete_permission(self, request, obj=None):
        return True  # ✅ Permiso para ELIMINAR
    
    def has_add_permission(self, request):
        return True  # ✅ Permiso para AGREGAR