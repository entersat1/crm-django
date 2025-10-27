from django.contrib import admin
from django.urls import path, include
from servicios.views import dashboard_power
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', dashboard_power, name='home'),
    path('admin/', admin.site.urls),
    path('servicios/', include('servicios.urls')),
    path('servicios/dashboard-power/', dashboard_power, name='dashboard_power'),
    path('sistema/inventario/', include('inventario.urls')),
    
    # ✅ DESCOMENTAR VENTAS:
    path('ventas/', include('ventas.urls')),  # ✅ ACTIVADO
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)