from django.urls import path
from .views import ficha_venta_pdf

app_name = 'ventas_taller'

urlpatterns = [
    path('ficha/<int:venta_id>/pdf/', ficha_venta_pdf, name='ficha_venta_pdf'),
]
