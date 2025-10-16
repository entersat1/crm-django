# ventas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La página para mostrar la interfaz del POS
    path('pos/', views.punto_de_venta, name='punto_de_venta'),
    
    # La nueva URL para procesar y guardar la venta
    path('registrar/', views.registrar_venta, name='registrar_venta'),
]