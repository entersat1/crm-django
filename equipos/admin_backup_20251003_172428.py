<<<<<<< HEAD
from django.contrib import admin

# 🎯 ADMIN MÍNIMO UNIVERSAL - NO FALLA NUNCA
def crear_admin_minimo(model):
    class ModelAdminMinimo(admin.ModelAdmin):
        def get_list_display(self, request):
            # Solo mostrar campos básicos que existen
            campos = []
            for field in model._meta.fields[:3]:  # Máximo 3 campos
                campos.append(field.name)
            return campos or ['__str__']
        
        def get_search_fields(self, request):
            # Solo buscar en campos de texto
            campos_busqueda = []
            for field in model._meta.fields:
                if field.get_internal_type() in ['CharField', 'TextField']:
                    campos_busqueda.append(field.name)
                    break
            return campos_busqueda or []
    
    return ModelAdminMinimo

# Registrar todos los modelos automáticamente
from django.apps import apps
app_config = apps.get_app_config('equipos')
for model in app_config.get_models():
    try:
        admin.site.register(model, crear_admin_minimo(model))
    except:
        pass  # Si falla, no registrar
=======
from django.contrib import admin

# 🎯 ADMIN MÍNIMO UNIVERSAL - NO FALLA NUNCA
def crear_admin_minimo(model):
    class ModelAdminMinimo(admin.ModelAdmin):
        def get_list_display(self, request):
            # Solo mostrar campos básicos que existen
            campos = []
            for field in model._meta.fields[:3]:  # Máximo 3 campos
                campos.append(field.name)
            return campos or ['__str__']
        
        def get_search_fields(self, request):
            # Solo buscar en campos de texto
            campos_busqueda = []
            for field in model._meta.fields:
                if field.get_internal_type() in ['CharField', 'TextField']:
                    campos_busqueda.append(field.name)
                    break
            return campos_busqueda or []
    
    return ModelAdminMinimo

# Registrar todos los modelos automáticamente
from django.apps import apps
app_config = apps.get_app_config('equipos')
for model in app_config.get_models():
    try:
        admin.site.register(model, crear_admin_minimo(model))
    except:
        pass  # Si falla, no registrar
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
