from django.urls import path
from . import views_gestion

app_name = 'inventario'

urlpatterns = [
    path('sistema-gestion/', views_gestion.sistema_gestion_productos, name='sistema_gestion'),
    path('api/gestion-productos/', views_gestion.api_gestion_productos, name='api_gestion_productos'),
]