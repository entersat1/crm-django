<<<<<<< HEAD
from django.urls import path
from .views import ficha_venta_pdf

app_name = 'ventas_taller'

urlpatterns = [
    path('ficha/<int:venta_id>/pdf/', ficha_venta_pdf, name='ficha_venta_pdf'),
]
=======
from django.urls import path
from .views import ficha_venta_pdf

app_name = 'ventas_taller'

urlpatterns = [
    path('ficha/<int:venta_id>/pdf/', ficha_venta_pdf, name='ficha_venta_pdf'),
]
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
