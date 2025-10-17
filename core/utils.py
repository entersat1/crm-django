import requests
import logging
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Sum, F
from datetime import timedelta

# Importamos los modelos que usaremos para las estadísticas
from servicios.models import OrdenTaller
from inventario.models import Producto
# from finanzas.models import Transaccion  # Comentado temporalmente

logger = logging.getLogger(__name__)

def get_dolar_blue():
    """
    Obtiene la cotización del dólar blue desde DolarAPI con caché.
    """
    dolar_cache = cache.get('cotizacion_dolar_blue')
    if dolar_cache:
        return dolar_cache
    try:
        response = requests.get('https://dolarapi.com/v1/dolares/blue', timeout=5)
        response.raise_for_status()
        data = response.json()
        cotizacion = {
            'valor_venta': float(data.get('venta', 0)),
            'fecha_actualizacion': timezone.now()
        }
        cache.set('cotizacion_dolar_blue', cotizacion, 900) # Guardar por 15 minutos
        return cotizacion
    except requests.RequestException as e:
        logger.warning(f"Fallo en la API del dólar: {e}")
        return {
            'valor_venta': 0.00,
            'fecha_actualizacion': timezone.now()
        }

def get_estadisticas_dashboard():
    """
    Calcula todas las estadísticas necesarias para el dashboard.
    """
    hoy = timezone.now()
    hace_30_dias = hoy - timedelta(days=30)
    primer_dia_mes = hoy.replace(day=1)
    estados_activos = ['recibido', 'diagnostico', 'espera_repuestos', 'reparacion']
    
    stats = {
        'ordenes_activas': OrdenTaller.objects.filter(estado__in=estados_activos).count(),
        # Comentado temporalmente hasta que arreglemos el modelo Transaccion
        'ingresos_mes': 0,  # Transaccion.objects.filter(tipo='ingreso', fecha__gte=hace_30_dias).aggregate(total=Sum('monto'))['total'] or 0,
        'balance_mes': 0,   # Transaccion.objects.filter(fecha__gte=hace_30_dias).aggregate(total=Sum('monto'))['total'] or 0,
        'stock_bajo': Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count(),
        'ordenes_completadas_mes': OrdenTaller.objects.filter(estado='finalizado', fecha_actualizacion__gte=primer_dia_mes).count(),
    }
    return stats