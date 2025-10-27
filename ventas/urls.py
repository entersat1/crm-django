<<<<<<< HEAD
from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.punto_de_venta, name='punto_de_venta'),
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    path('api/productos/<int:producto_id>/precio/', views.obtener_precio_producto, name='obtener_precio_producto'),
=======
# ventas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La página para mostrar la interfaz del POS
    path('pos/', views.punto_de_venta, name='punto_de_venta'),
    
    # La nueva URL para procesar y guardar la venta
    path('registrar/', views.registrar_venta, name='registrar_venta'),
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
]