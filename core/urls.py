from django.contrib import admin
from django.urls import path, include
from servicios.views import dashboard_power
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 🎯 Página principal
    path('', dashboard_power, name='home'),
    
    # ⚙️ Admin Django
    path('admin/', admin.site.urls),
    
    # 🛠️ Servicios
    path('servicios/', include('servicios.urls')),
    path('servicios/dashboard-power/', dashboard_power, name='dashboard_power'),
    
    # 🚀 SISTEMA DE GESTIÓN (Subdominio: sistema.zonalitoral.com.ar)
    path('sistema/inventario/', include('inventario.urls')),  # ✅ DESCOMENTADA - AHORA ACTIVA
    
    # 📦 SOLO las apps que SÍ tienen urls.py - COMENTA LAS QUE FALTAN
    # path('ventas/', include('ventas.urls')),  # ⛔ COMENTADO - No existe ventas/urls.py
    # path('clientes/', include('clientes.urls')),  # ⛔ COMENTADO - No existe clientes/urls.py
    # path('finanzas/', include('finanzas.urls')),  # ⛔ COMENTADO - No existe finanzas/urls.py
    # path('marketing/', include('marketing.urls')),  # ⛔ COMENTADO - No existe marketing/urls.py
]

# ✅ SERVIR ARCHIVOS MEDIA EN DESARROLLO
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)