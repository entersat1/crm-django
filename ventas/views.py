<<<<<<< HEAD
import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Venta, DetalleVenta
from clientes.models import Cliente
from inventario.models import Producto, CotizacionDolar
from finanzas.models import Transaccion

@login_required
def punto_de_venta(request):
    productos = Producto.objects.filter(activo=True)
    clientes = Cliente.objects.all()
    
    # ✅ AGREGADO: Obtener la cotización
    cotizacion_actual = CotizacionDolar.obtener_cotizacion_actual()
    valor_dolar = cotizacion_actual.valor_venta
    
    context = {
        'productos': productos, 
        'clientes': clientes,
        'valor_dolar_actual': valor_dolar  # <-- ✅ Pasar el dólar al template
    }
    return render(request, 'ventas/punto_de_venta.html', context)
@login_required
@transaction.atomic
def registrar_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente_id = data.get('cliente')
            carrito = data.get('carrito')

            cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None

            # OBTENER COTIZACIÓN ACTUAL DEL DÓLAR
            cotizacion_actual = CotizacionDolar.obtener_cotizacion_actual()
            
            # 1. Creamos la Venta CON LA COTIZACIÓN CORRECTA
            nueva_venta = Venta.objects.create(
                cliente=cliente, 
                total=0,
                cotizacion_dolar=cotizacion_actual.valor_venta
            )
            total_venta = 0

            # 2. Creamos los Detalles y descontamos stock
            for producto_id, item in carrito.items():
                producto = Producto.objects.get(id=producto_id)
                cantidad = int(item['cantidad'])
                
                if producto.stock_actual < cantidad:
                    raise Exception(f"No hay stock suficiente para {producto.nombre}")
                
                producto.stock_actual -= cantidad
                producto.save()

                # ✅ CORREGIDO: Campos del modelo DetalleVenta
                precio_unitario = getattr(producto, 'precio_venta_usd', 0) or getattr(producto, 'precio_venta_actual', 0)
                
                detalle = DetalleVenta.objects.create(
                    venta=nueva_venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario_usd=precio_unitario,
                    descuento_usd=0,
                    subtotal_usd=precio_unitario * cantidad,
                    subtotal_en_pesos=(precio_unitario * cantidad) * cotizacion_actual.valor_venta
                )
                total_venta += detalle.subtotal_en_pesos

            # 3. Actualizamos el total y creamos la transacción
            nueva_venta.total = total_venta
            nueva_venta.save()
            
            Transaccion.objects.create(
                tipo='ingreso',
                monto=total_venta,
                descripcion=f'Ingreso por Venta #{nueva_venta.id}'
            )
            
            return JsonResponse({'status': 'success', 'venta_id': nueva_venta.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

@login_required
def obtener_precio_producto(request, producto_id):
    """API simple para obtener el precio de un producto"""
    try:
        producto = Producto.objects.get(id=producto_id)
        precio_venta_usd = getattr(producto, 'precio_venta_usd', 0) or getattr(producto, 'precio_venta_actual', 0)
        
        return JsonResponse({
            'precio_venta_usd': float(precio_venta_usd or 0),
            'nombre': producto.nombre
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
=======
import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Venta, DetalleVenta
from clientes.models import Cliente
from inventario.models import Producto
from finanzas.models import Transaccion

@login_required
def punto_de_venta(request):
    productos = Producto.objects.filter(activo=True)
    clientes = Cliente.objects.all()
    context = {'productos': productos, 'clientes': clientes}
    return render(request, 'ventas/punto_de_venta.html', context)

@login_required
@transaction.atomic # Esto asegura que toda la operación sea a prueba de errores
def registrar_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente_id = data.get('cliente')
            carrito = data.get('carrito')

            cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None

            # 1. Creamos la Venta
            nueva_venta = Venta.objects.create(cliente=cliente, total=0)
            total_venta = 0

            # 2. Creamos los Detalles y descontamos stock
            for producto_id, item in carrito.items():
                producto = Producto.objects.get(id=producto_id)
                cantidad = int(item['cantidad'])
                
                if producto.stock_actual < cantidad:
                    raise Exception(f"No hay stock suficiente para {producto.nombre}")
                
                producto.stock_actual -= cantidad
                producto.save()

                detalle = DetalleVenta.objects.create(
                    venta=nueva_venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta_actual
                )
                total_venta += detalle.subtotal

            # 3. Actualizamos el total y creamos la transacción
            nueva_venta.total = total_venta
            nueva_venta.save()
            
            Transaccion.objects.create(
                tipo='ingreso',
                monto=total_venta,
                descripcion=f'Ingreso por Venta #{nueva_venta.id}'
            )
            
            return JsonResponse({'status': 'success', 'venta_id': nueva_venta.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
