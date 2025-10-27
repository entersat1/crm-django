<<<<<<< HEAD
from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_campana, name='crear_campana_marketing'),
    # Aquí añadiremos más rutas de marketing en el futuro
=======
from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_campana, name='crear_campana_marketing'),
    # Aquí añadiremos más rutas de marketing en el futuro
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
]