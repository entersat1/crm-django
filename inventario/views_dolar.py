<<<<<<< HEAD
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import CotizacionDolar, Producto

@login_required
def panel_control_dolar(request):
    """Panel de control para gestión del dólar"""
    cotizacion_actual = CotizacionDolar.obtener_cotizacion_actual()
    
    if request.method == 'POST':
        try:
            valor_compra = float(request.POST.get('valor_compra', 0))
            valor_venta = float(request.POST.get('valor_venta', 0))
            actualizar_precios = request.POST.get('actualizar_precios') == 'on'
            
            if valor_venta > 0:
                nueva_cotizacion = CotizacionDolar(
                    valor_compra=valor_compra,
                    valor_venta=valor_venta,
                    fuente='Manual',
                    activo=True
                )
                nueva_cotizacion.save()
                
                mensaje = f'✅ Dólar actualizado: Compra ${valor_compra} - Venta ${valor_venta}'
                
                if actualizar_precios:
                    # Actualizar precios de productos
                    from django.core.management import call_command
                    call_command('actualizar_precios_dolar', '--forzar')
                    mensaje += ' - Precios de productos actualizados'
                
                messages.success(request, mensaje)
            
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
        
        return redirect('panel_control_dolar')
    
    # Estadísticas
    total_productos = Producto.objects.filter(activo=True).count()
    productos_con_precio_compra = Producto.objects.filter(activo=True, precio_compra_usd__gt=0).count()
    
    context = {
        'cotizacion_actual': cotizacion_actual,
        'total_productos': total_productos,
        'productos_con_precio_compra': productos_con_precio_compra,
    }
    
    return render(request, 'inventario/panel_dolar.html', context)

@login_required
def actualizar_dolar_automatico(request):
    """Actualizar dólar automáticamente desde API"""
    try:
        cotizacion = CotizacionDolar.actualizar_desde_api()
        if cotizacion:
            return JsonResponse({
                'status': 'success',
                'compra': float(cotizacion.valor_compra),
                'venta': float(cotizacion.valor_venta),
                'fuente': cotizacion.fuente
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No se pudo obtener la cotización automática'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
=======
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import CotizacionDolar, Producto

@login_required
def panel_control_dolar(request):
    """Panel de control para gestión del dólar"""
    cotizacion_actual = CotizacionDolar.obtener_cotizacion_actual()
    
    if request.method == 'POST':
        try:
            valor_compra = float(request.POST.get('valor_compra', 0))
            valor_venta = float(request.POST.get('valor_venta', 0))
            actualizar_precios = request.POST.get('actualizar_precios') == 'on'
            
            if valor_venta > 0:
                nueva_cotizacion = CotizacionDolar(
                    valor_compra=valor_compra,
                    valor_venta=valor_venta,
                    fuente='Manual',
                    activo=True
                )
                nueva_cotizacion.save()
                
                mensaje = f'✅ Dólar actualizado: Compra ${valor_compra} - Venta ${valor_venta}'
                
                if actualizar_precios:
                    # Actualizar precios de productos
                    from django.core.management import call_command
                    call_command('actualizar_precios_dolar', '--forzar')
                    mensaje += ' - Precios de productos actualizados'
                
                messages.success(request, mensaje)
            
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
        
        return redirect('panel_control_dolar')
    
    # Estadísticas
    total_productos = Producto.objects.filter(activo=True).count()
    productos_con_precio_compra = Producto.objects.filter(activo=True, precio_compra_usd__gt=0).count()
    
    context = {
        'cotizacion_actual': cotizacion_actual,
        'total_productos': total_productos,
        'productos_con_precio_compra': productos_con_precio_compra,
    }
    
    return render(request, 'inventario/panel_dolar.html', context)

@login_required
def actualizar_dolar_automatico(request):
    """Actualizar dólar automáticamente desde API"""
    try:
        cotizacion = CotizacionDolar.actualizar_desde_api()
        if cotizacion:
            return JsonResponse({
                'status': 'success',
                'compra': float(cotizacion.valor_compra),
                'venta': float(cotizacion.valor_venta),
                'fuente': cotizacion.fuente
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No se pudo obtener la cotización automática'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
        })