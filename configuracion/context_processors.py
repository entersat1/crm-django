from .models import Empresa

def configuracion_global(request):
    """
    Hace que los datos de la empresa estén disponibles en todas las plantillas.
    """
    # Usamos get_or_create para obtener la única instancia de configuración,
    # o crearla si es la primera vez que se ejecuta.
    datos_empresa, created = Empresa.objects.get_or_create(pk=1)
    return {'config_negocio': datos_empresa}