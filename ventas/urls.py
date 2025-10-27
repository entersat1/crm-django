# ventas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La página para mostrar la interfaz del POS
    path('pos/', views.punto_de_venta, name='punto_de_venta'),
    
    # La nueva URL para procesar y guardar la venta
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    
    # ✅ AGREGAR ESTO - API para obtener precios de productos
    path('api/productos/<int:producto_id>/precio/', views.obtener_precio_producto, name='obtener_precio_producto'),
]