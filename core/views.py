from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F

# Importamos los modelos y las funciones que necesitamos
from servicios.models import OrdenTaller
from inventario.models import Producto
from .utils import get_dolar_blue, get_estadisticas_dashboard

@login_required
def dashboard(request):
    """
    Vista principal que muestra un resumen completo del sistema.
    """
    # Usamos nuestras funciones del archivo utils.py
    stats = get_estadisticas_dashboard()
    cotizacion_dolar = get_dolar_blue()
    
    # Obtenemos los datos para las listas directamente en la vista
    ordenes_recientes = OrdenTaller.objects.order_by('-fecha_creacion')[:5]
    productos_criticos = Producto.objects.filter(stock_actual__lte=F('stock_minimo'))[:5]

    context = {
        'stats': stats,
        'ordenes_recientes': ordenes_recientes,
        'productos_criticos': productos_criticos,
        'cotizacion_dolar': cotizacion_dolar,
    }
    
    return render(request, 'dashboard.html', context)
# =============================================================================
# VISTAS DE ERROR PERSONALIZADAS
# =============================================================================

def custom_404_view(request, exception):
    """Vista personalizada para error 404."""
    return render(request, '404.html', status=404)

def custom_500_view(request):
    """Vista personalizada para error 500."""
    return render(request, '500.html', status=500)

def custom_403_view(request, exception):
    """Vista personalizada para error 403."""
    return render(request, '403.html', status=403)

def custom_400_view(request, exception):
    """Vista personalizada para error 400."""
    return render(request, '400.html', status=400)

def test_404(request):
    """Vista para probar el template 404 personalizado en desarrollo."""
    return render(request, '404.html', status=404)
