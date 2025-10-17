from django.urls import path
from . import views

app_name = 'servicios'

urlpatterns = [
    # DASHBOARD - CON EL NOMBRE ORIGINAL
    path('dashboard-power/', views.dashboard_power, name='dashboard_power'),
    
    # ACCIONES DE ÓRDENES
    path('orden/imprimir/<int:orden_id>/', views.imprimir_orden_unificada, name='imprimir_orden_unificada'),
    path('orden/whatsapp/<int:orden_id>/', views.enviar_whatsapp_unificada, name='enviar_whatsapp_unificada'),
    path('orden/email/<int:orden_id>/', views.enviar_email_unificada, name='enviar_email_unificada'),
    
    # ACTUALIZAR DÓLAR
    path('actualizar-dolar/', views.actualizar_dolar, name='actualizar_dolar'),
    
    # LISTAR ÓRDENES
    path('ordenes/', views.listar_ordenes_dashboard, name='ver_ordenes'),
    
    # REDIRECCIONES AL ADMIN
    path('admin/ordenes/', views.redirigir_admin_ordenes, name='redirigir_admin_ordenes'),
    path('admin/productos/', views.redirigir_admin_productos, name='redirigir_admin_productos'),
    path('admin/clientes/', views.redirigir_admin_clientes, name='redirigir_admin_clientes'),
    path('admin/ventas/', views.redirigir_admin_ventas, name='redirigir_admin_ventas'),
    path('admin/finanzas/', views.redirigir_admin_finanzas, name='redirigir_admin_finanzas'),
    path('admin/panel/', views.redirigir_panel_admin, name='redirigir_panel_admin'),
    path('crear-orden/', views.redirigir_crear_orden, name='crear_orden'),
]