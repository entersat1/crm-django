import requests
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count, Q, F
from urllib.parse import quote
from .models import OrdenTaller, ItemReparacion
from configuracion.models import Empresa as ConfiguracionNegocio
from inventario.models import Producto, CotizacionDolar
from ventas.models import Venta
from clientes.models import Cliente
from datetime import datetime, timedelta

def obtener_dolar_blue():
    """Obtener cotización del dólar blue automáticamente"""
    try:
        # API 1: DolarSi (oficial)
        response = requests.get('https://www.dolarsi.com/api/api.php?type=valoresprincipales', timeout=10)
        if response.status_code == 200:
            datos = response.json()
            for item in datos:
                if 'blue' in item['casa']['nombre'].lower():
                    return float(item['casa']['venta'].replace(',', '.'))
    except:
        pass
    
    try:
        # API 2: Bluelytics (fallback)
        response = requests.get('https://api.bluelytics.com.ar/v2/latest', timeout=10)
        if response.status_code == 200:
            datos = response.json()
            return float(datos['blue']['value_sell'])
            
    except:
        pass
    
    return None

def calcular_estadisticas_financieras(mes, anio):
    """Calcula las estadísticas financieras para un mes y año dados."""
    return {
        'ingresos': 1500000,
        'gastos': 500000,
        'ganancias': 1000000,
        'margen_ganancia': 66.67
    }

@login_required
def dashboard_power(request):
    """Dashboard principal con dólar y finanzas"""
    
    config = ConfiguracionNegocio.objects.first()
    
    # ⬇️ Obtener cotización REAL de la base de datos
    try:
        cotizacion_db = CotizacionDolar.obtener_cotizacion_actual()
        cotizacion_dolar = {
            'valor': cotizacion_db.valor_venta,
            'fuente': cotizacion_db.fuente, 
            'fecha_actualizacion': cotizacion_db.fecha_actualizacion.strftime("%d/%m/%Y %H:%M"),
            'automatico': cotizacion_db.fuente != 'Manual'
        }
    except Exception as e:
        # Fallback si no existe cotización o hay un error
        cotizacion_dolar = {
            'valor': 1400.00,
            'fuente': 'Manual', 
            'fecha_actualizacion': timezone.now().strftime("%d/%m/%Y %H:%M"),
            'automatico': False
        }
    
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year
    
    # ⬇️ CALCULANDO TODAS LAS MÉTRICAS NECESARIAS ⬇️
    
    # Métricas de Órdenes
    ordenes_totales = OrdenTaller.objects.count()
    ordenes_activas = OrdenTaller.objects.exclude(
        estado__in=['completado', 'entregado', 'cancelado']
    ).count()
    ordenes_completadas_mes = OrdenTaller.objects.filter(
        estado='completado',
        fecha_ingreso__month=mes_actual,
        fecha_ingreso__year=anio_actual
    ).count()
    ordenes_urgentes = OrdenTaller.objects.filter(prioridad='urgente').count()
    ultimas_ordenes = OrdenTaller.objects.all().order_by('-fecha_ingreso')[:10]
    
    # Métricas de Inventario
    total_productos = Producto.objects.count()
    productos_web_count = Producto.objects.filter(publicado_web=True).count()
    stock_bajo_count = Producto.objects.filter(stock_actual__lte=5).count()
    stock_critico_count = Producto.objects.filter(stock_actual=0).count()
    
    # Métricas de Ventas
    hoy = timezone.now().date()
    ventas_hoy = Venta.objects.filter(
        fecha_venta__date=hoy
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Métricas de Clientes
    total_clientes = Cliente.objects.count()

    # Métricas Financieras (usando una función simulada temporalmente)
    finanzas = calcular_estadisticas_financieras(mes_actual, anio_actual)

    # Contexto para la plantilla
    context = {
        'hoy': timezone.now().strftime("%d/%m/%Y"),
        'config': config,
        'cotizacion_dolar': cotizacion_dolar,
        
        # Dashboard Power
        'ordenes_totales': ordenes_totales,
        'ordenes_activas': ordenes_activas,
        'ordenes_pendientes': ordenes_activas,
        'ordenes_urgentes': ordenes_urgentes,
        'productos_web_count': productos_web_count,
        'stock_bajo_count': stock_bajo_count,
        'stock_critico_count': stock_critico_count,
        'ventas_hoy': ventas_hoy,
        'total_clientes': total_clientes,
        'ordenes_completadas_mes': ordenes_completadas_mes,
        'ingresos_mes': finanzas['ingresos'],
        'utilidad_mes': finanzas['ganancias'],

        # Para las tablas
        'ordenes': ultimas_ordenes,
        'mostrar_botones': True,
        'productos_criticos': Producto.objects.filter(stock_actual__lte=F('stock_minimo')),
    }
    
    return render(request, 'servicios/dashboard_power.html', context)

@login_required
def actualizar_dolar(request):
    """Actualizar dólar automáticamente desde APIs"""
    try:
        nuevo_valor = obtener_dolar_blue()
        
        if nuevo_valor:
            # Guardar en la base de datos (en inventario o configuracion)
            from inventario.models import CotizacionDolar
            cotizacion = CotizacionDolar.obtener_cotizacion_actual()
            cotizacion.valor_venta = nuevo_valor
            cotizacion.fuente = 'Automático API'
            cotizacion.save()
            
            messages.success(request, f'✅ Dólar actualizado: ${nuevo_valor}')
        else:
            messages.error(request, '❌ No se pudo obtener el dólar automáticamente')
            
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    
    return redirect('servicios:dashboard_power')

def redirigir_admin_ordenes(request):
    return redirect('/admin/servicios/ordentaller/')

def redirigir_admin_productos(request):
    return redirect('/admin/inventario/producto/')

def redirigir_admin_clientes(request):
    return redirect('/admin/clientes/cliente/')

def redirigir_admin_ventas(request):
    return redirect('/admin/ventas/venta/')

def redirigir_admin_finanzas(request):
    return redirect('/admin/servicios/gasto/')

# 📍 EDITÁ /opt/crm-django/servicios/views.py
# REEMPLAZÁ la función crear_orden actual por:

@login_required
def crear_orden(request):
    """Redirigir al formulario de crear orden en el admin"""
    return redirect('/admin/servicios/ordentaller/add/')

@login_required  
def ver_ordenes(request):
    """Redirigir al listado de órdenes en el admin"""
    return redirect('/admin/servicios/ordentaller/')

@login_required
def imprimir_orden_unificada(request, orden_id):
    """Vista de IMPRIMIR - funciona en admin y dashboard"""
    orden = get_object_or_404(OrdenTaller, id=orden_id)
    config = ConfiguracionNegocio.objects.first()
    
    # ✅ CORREGIDO - usar campos reales
    costo_productos = sum(p.subtotal for p in orden.repuestos_usados.all())
    costo_total = orden.costo_final + costo_productos
    
    # ✅ CORREGIDO - SIN F-STRING PROBLEMÁTICO
    logo_html = ""
    if config and config.logo:
        logo_html = f"<img src='/media/{config.logo}' style='max-height: 80px; margin-bottom: 10px;' alt='{config.nombre}'>"
    else:
        logo_html = f"<h1>{config.nombre if config else 'TALLER TÉCNICO'}</h1>"
    
    negocio_info = ""
    if config:
        negocio_info = f'<div class="negocio-info"><p><strong>{config.nombre}</strong><br>{config.direccion}<br>📞 {config.telefono} | 📧 {config.email}</p></div>'
    
    repuestos_html = ""
    if orden.repuestos_usados.exists():
        repuestos_items = ""
        for item in orden.repuestos_usados.all():
            repuestos_items += f"<div class=\"producto\"><strong>{item.producto.nombre}</strong> - {item.cantidad} x ${item.precio_unitario} = <strong>${item.subtotal:.2f}</strong></div>"
        repuestos_html = f"<div class=\"section\"><h3>📦 REPUESTOS UTILIZADOS</h3>{repuestos_items}</div>"
    
    costo_repuestos_html = ""
    if orden.repuestos_usados.exists():
        costo_repuestos_html = f"<div class=\"row\"><span class=\"label\">Costo repuestos:</span><span class=\"valor\">${costo_productos:.2f}</span></div>"
    
    html = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Orden #{orden.numero_orden}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.4; }}
            .header {{ text-align: center; border-bottom: 3px solid #333; padding-bottom: 15px; margin-bottom: 20px; }}
            .negocio-info {{ text-align: center; margin-bottom: 20px; font-size: 14px; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .section h3 {{ background: #f8f9fa; padding: 10px; margin: -15px -15px 15px -15px; border-bottom: 1px solid #ddd; }}
            .row {{ display: flex; justify-content: space-between; margin: 8px 0; }}
            .label {{ font-weight: bold; min-width: 150px; }}
            .valor {{ flex: 1; }}
            .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 10px; }}
            .producto {{ border-left: 4px solid #3498db; padding-left: 10px; margin: 5px 0; }}
            .codigo-consulta {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0; }}
            @media print {{
                body {{ margin: 0; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            {logo_html}
            <h2>ORDEN DE REPARACIÓN N° {orden.numero_orden}</h2>
            <p><strong>Fecha de ingreso:</strong> {orden.fecha_ingreso.strftime("%d/%m/%Y %H:%M")}</p>
        </div>
        
        {negocio_info}
        
        <div class="section">
            <h3>👤 INFORMACIÓN DEL CLIENTE</h3>
            <div class="row">
                <span class="label">Nombre:</span>
                <span class="valor">{orden.cliente.nombre}</span>
            </div>
            <div class="row">
                <span class="label">Teléfono:</span>
                <span class="valor">{orden.cliente.telefono}</span>
            </div>
            <div class="row">
                <span class="label">Email:</span>
                <span class="valor">{orden.cliente.email or "No especificado"}</span>
            </div>
        </div>
        
        <div class="section">
            <h3>🔧 INFORMACIÓN DEL EQUIPO</h3>
            <div class="row">
                <span class="label">Equipo:</span>
                <span class="valor">{orden.equipo}</span>
            </div>
            <div class="row">
                <span class="label">Número de Serie:</span>
                <span class="valor">{orden.numero_serie or "No especificado"}</span>
            </div>
            <div class="row">
                <span class="label">Problema reportado:</span>
                <span class="valor">{orden.problema}</span>
            </div>
            <div class="row">
                <span class="label">Accesorios:</span>
                <span class="valor">{orden.accesorios or "Ninguno especificado"}</span>
            </div>
        </div>
        
        <div class="section">
            <h3>⚙️ DIAGNÓSTICO Y REPARACIÓN</h3>
            <div class="row">
                <span class="label">Estado:</span>
                <span class="valor">{orden.get_estado_display()}</span>
            </div>
            <div class="row">
                <span class="label">Diagnóstico:</span>
                <span class="valor">{orden.diagnostico or "Pendiente de diagnóstico"}</span>
            </div>
            <div class="row">
                <span class="label">Solución:</span>
                <span class="valor">{orden.solucion or "Pendiente"}</span>
            </div>
            <div class="row">
                <span class="label">Observaciones:</span>
                <span class="valor">{orden.observaciones or "Ninguna"}</span>
            </div>
        </div>
        
        {repuestos_html}
        
        <div class="section">
            <h3>💰 INFORMACIÓN ECONÓMICA</h3>
            <div class="row">
                <span class="label">Presupuesto:</span>
                <span class="valor">${orden.presupuesto}</span>
            </div>
            <div class="row">
                <span class="label">Costo mano de obra:</span>
                <span class="valor">${orden.costo_final}</span>
            </div>
            {costo_repuestos_html}
            <div class="row">
                <span class="label">Costo total:</span>
                <span class="valor"><strong>${costo_total:.2f}</strong></span>
            </div>
        </div>
        
        <div class="footer">
            <p>Documento generado el {timezone.now().strftime("%d/%m/%Y a las %H:%M")} - {config.nombre if config else "Sistema de Gestión de Taller"}</p>
            <p>Página 1/1</p>
        </div>
        
        <div class="no-print" style="margin-top: 20px; text-align: center;">
            <button onclick="window.print()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">
                🖨️ Imprimir
            </button>
            <button onclick="window.close()" style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px;">
                ❌ Cerrar
            </button>
        </div>
    </body>
    </html>
    '''
    
    response = HttpResponse(html)
    response['Content-Disposition'] = f'filename="orden_{orden.numero_orden}.html"'
    return response

@login_required
def enviar_email_unificada(request, orden_id):
    """ENVIAR EMAIL - funciona en admin y dashboard"""
    orden = get_object_or_404(OrdenTaller, id=orden_id)
    config = ConfiguracionNegocio.objects.first()
    
    # ✅ CORREGIDO - usar campos reales
    costo_productos = sum(p.subtotal for p in orden.repuestos_usados.all())
    costo_total = orden.costo_final + costo_productos
    
    messages.success(request, f' Email listo para enviar - Orden {orden.numero_orden}')
    messages.info(request, f' Cliente: {orden.cliente.nombre}')
    messages.info(request, f' Email: {orden.cliente.email or "No registrado"}')
    messages.info(request, f' Costo total: ${costo_total}')
    if hasattr(orden, 'codigo_consulta') and orden.codigo_consulta:
        messages.info(request, f' Código consulta: {orden.codigo_consulta}')
    messages.warning(request, 'Para enviar emails reales configure SMTP en settings.py')
    
    return redirect('servicios:dashboard_power')

@login_required
def enviar_whatsapp_unificada(request, orden_id):
    """ENVIAR WHATSAPP - funciona en admin y dashboard"""
    orden = get_object_or_404(OrdenTaller, id=orden_id)
    config = ConfiguracionNegocio.objects.first()
    
    # ✅ ACTUALIZAR ESTADO A COMPLETADO
    if orden.estado != 'completado':
        orden.estado = 'completado'
        orden.save()
    
    # ✅ CORREGIDO - usar campos reales
    costo_productos = sum(p.subtotal for p in orden.repuestos_usados.all())
    costo_total = orden.costo_final + costo_productos
    
    # ✅ CORREGIDO - SIN F-STRING PROBLEMÁTICO
    mensaje_lines = [
        f"Hola {orden.cliente.nombre}!",
        "",
        f"*REPARACIÓN COMPLETADA - {config.nombre if config else 'Taller Técnico'}*",
        "",
        f"*Orden:* {orden.numero_orden}",
        f"*Equipo:* {orden.equipo}",
        "✅ *Estado:* COMPLETADO",
        "",
        "*Problema resuelto:*",
        orden.problema,
        "",
        "*Solución aplicada:*",
        orden.solucion or "Reparación técnica completada",
        ""
    ]

    # Agregar repuestos si existen
    if orden.repuestos_usados.exists():
        mensaje_lines.append("*Repuestos utilizados:*")
        for p in orden.repuestos_usados.all():
            mensaje_lines.append(f" - {p.producto.nombre} x{p.cantidad} - ${p.subtotal}")
        mensaje_lines.append("")

    # Información económica
    mensaje_lines.extend([
        "*Información económica:*",
        f"💰 Presupuesto: ${orden.presupuesto}",
        f"💵 Costo total: ${costo_total}",
        f"🎫 Seña: ${orden.seña}",
        f"📊 Saldo: ${costo_total - orden.seña}",
        "",
        "*¡Tu equipo está listo para retirar!*",
        ""
    ])

    if orden.codigo_consulta:
        mensaje_lines.append(f"Consulta el estado con el código: {orden.codigo_consulta}")
        mensaje_lines.append("")

    mensaje_lines.extend([
        "Saludos cordiales,",
        config.nombre if config else "Taller Técnico"
    ])

    mensaje = "\n".join(mensaje_lines)
    
    telefono_limpio = ''.join(c for c in orden.cliente.telefono if c.isdigit())
    url_whatsapp = f'https://wa.me/{telefono_limpio}?text={quote(mensaje)}'
    
    # ✅ REDIRIGIR DIRECTAMENTE A WHATSAPP
    return redirect(url_whatsapp)

@login_required
def listar_ordenes_dashboard(request):
    """Vista para listar órdenes en el dashboard con botones"""
    ordenes = OrdenTaller.objects.all().order_by('-fecha_ingreso')
    
    context = {
        'ordenes': ordenes,
        'total_ordenes': ordenes.count(),
        'mostrar_botones': True,
        'hoy': timezone.now().strftime("%d/%m/%Y")
    }
    return render(request, 'servicios/listar_ordenes.html', context)