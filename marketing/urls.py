from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_campana, name='crear_campana_marketing'),
    # Aquí añadiremos más rutas de marketing en el futuro
]