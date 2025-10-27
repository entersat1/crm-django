from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.punto_de_venta, name='punto_de_venta'),
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    path('api/productos/<int:producto_id>/precio/', views.obtener_precio_producto, name='obtener_precio_producto'),
]