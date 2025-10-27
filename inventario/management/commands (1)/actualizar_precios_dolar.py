<<<<<<< HEAD
from django.core.management.base import BaseCommand
from django.utils import timezone
from inventario.models import CotizacionDolar, Producto

class Command(BaseCommand):
    help = 'Actualizar precios de productos según el dólar actual'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Forzar actualización incluso si el dólar no cambió',
        )
        parser.add_argument(
            '--margen',
            type=float,
            default=0.30,
            help='Margen de ganancia a aplicar (ej: 0.30 para 30%%)',
        )

    def handle(self, *args, **options):
        forzar = options['forzar']
        margen = options['margen']
        
        # Obtener cotización actual
        cotizacion_actual = CotizacionDolar.obtener_cotizacion_actual()
        
        if not cotizacion_actual:
            self.stdout.write(
                self.style.ERROR('❌ No hay cotización de dólar activa')
            )
            return
        
        self.stdout.write(f'💰 Cotización actual: Compra ${cotizacion_actual.valor_compra} - Venta ${cotizacion_actual.valor_venta}')
        
        # Contadores
        productos_actualizados = 0
        productos_con_error = 0
        
        # Actualizar productos
        productos = Producto.objects.filter(activo=True, precio_compra_usd__gt=0)
        
        for producto in productos:
            try:
                # Calcular nuevo precio de venta en USD manteniendo el margen
                precio_venta_anterior = producto.precio_venta_usd
                nuevo_precio_venta_usd = round(producto.precio_compra_usd * (1 + margen), 2)
                
                # Solo actualizar si el precio cambió o se fuerza
                if forzar or nuevo_precio_venta_usd != precio_venta_anterior:
                    producto.precio_venta_usd = nuevo_precio_venta_usd
                    producto.save()
                    productos_actualizados += 1
                    
                    self.stdout.write(
                        f'✅ {producto.nombre}: '
                        f'Compra USD ${producto.precio_compra_usd} → '
                        f'Venta USD ${nuevo_precio_venta_usd} '
                        f'(ARS ${producto.precio_venta_ars})'
                    )
                
            except Exception as e:
                productos_con_error += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Error en {producto.nombre}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎯 Actualización completada: '
                f'{productos_actualizados} productos actualizados, '
                f'{productos_con_error} errores'
            )
=======
from django.core.management.base import BaseCommand
from django.utils import timezone
from inventario.models import CotizacionDolar, Producto

class Command(BaseCommand):
    help = 'Actualizar precios de productos según el dólar actual'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Forzar actualización incluso si el dólar no cambió',
        )
        parser.add_argument(
            '--margen',
            type=float,
            default=0.30,
            help='Margen de ganancia a aplicar (ej: 0.30 para 30%%)',
        )

    def handle(self, *args, **options):
        forzar = options['forzar']
        margen = options['margen']
        
        # Obtener cotización actual
        cotizacion_actual = CotizacionDolar.obtener_cotizacion_actual()
        
        if not cotizacion_actual:
            self.stdout.write(
                self.style.ERROR('❌ No hay cotización de dólar activa')
            )
            return
        
        self.stdout.write(f'💰 Cotización actual: Compra ${cotizacion_actual.valor_compra} - Venta ${cotizacion_actual.valor_venta}')
        
        # Contadores
        productos_actualizados = 0
        productos_con_error = 0
        
        # Actualizar productos
        productos = Producto.objects.filter(activo=True, precio_compra_usd__gt=0)
        
        for producto in productos:
            try:
                # Calcular nuevo precio de venta en USD manteniendo el margen
                precio_venta_anterior = producto.precio_venta_usd
                nuevo_precio_venta_usd = round(producto.precio_compra_usd * (1 + margen), 2)
                
                # Solo actualizar si el precio cambió o se fuerza
                if forzar or nuevo_precio_venta_usd != precio_venta_anterior:
                    producto.precio_venta_usd = nuevo_precio_venta_usd
                    producto.save()
                    productos_actualizados += 1
                    
                    self.stdout.write(
                        f'✅ {producto.nombre}: '
                        f'Compra USD ${producto.precio_compra_usd} → '
                        f'Venta USD ${nuevo_precio_venta_usd} '
                        f'(ARS ${producto.precio_venta_ars})'
                    )
                
            except Exception as e:
                productos_con_error += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Error en {producto.nombre}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎯 Actualización completada: '
                f'{productos_actualizados} productos actualizados, '
                f'{productos_con_error} errores'
            )
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
        )