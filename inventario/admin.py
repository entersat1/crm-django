from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.utils.html import format_html
from django.db.models import Sum, F, Value, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce
from django.db import transaction
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
import pandas as pd
import re
import unicodedata
import xml.etree.ElementTree as ET
import logging
import requests
from bs4 import BeautifulSoup
import json
from django.utils.text import slugify
from django.middleware.csrf import get_token
from .models import Producto, CategoriaProducto, CotizacionDolar, ClaseEquipo, MarcaEquipo, ModeloEquipo, ImagenProducto

logger = logging.getLogger(__name__)

# ✅ IMPORTADOR MEJORADO - MÁS PRODUCTOS + MEJOR DETECCIÓN
class ImportadorWebAutomatico:
    def __init__(self):
        self.base_url = "https://www.zonalitoral.com.ar"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def obtener_cotizacion_dolar(self):
        """Obtiene la cotización del dólar actual"""
        try:
            ultima_cotizacion = CotizacionDolar.objects.filter(activa=True).last()
            if ultima_cotizacion:
                return ultima_cotizacion.valor_venta
            else:
                return 1000.0
        except:
            return 1000.0
    
    def extraer_productos_desde_url(self, url):
        """Extrae productos de una URL específica - VERSIÓN MEJORADA"""
        try:
            print(f"🔍 Conectando a: {url}")
            response = self.session.get(url, timeout=20)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            productos = []
            
            # BUSQUEDA MÁS AGRESIVA DE PRODUCTOS
            selectores_posibles = [
                'div', 'article', 'li', 'section',
                '[class*="product"]', '[class*="item"]', '[class*="card"]',
                '[class*="producto"]', '[class*="articulo"]'
            ]
            
            items_producto = []
            for selector in selectores_posibles:
                try:
                    encontrados = soup.select(selector)
                    for item in encontrados:
                        texto = item.get_text()
                        # Si contiene signo de pesos y algo que parezca un producto
                        if '$' in texto and len(texto) < 1000:
                            items_producto.append(item)
                except:
                    continue
            
            print(f"📦 Elementos encontrados para analizar: {len(items_producto)}")
            
            # Procesar MÁS productos (100 en lugar de 30)
            for item in items_producto[:100]:
                producto_data = self._extraer_datos_producto_mejorado(item)
                if producto_data and producto_data.get('nombre') and producto_data.get('precio_pesos', 0) > 0:
                    productos.append(producto_data)
                    print(f"✅ Producto: {producto_data['nombre']} - ${producto_data['precio_pesos']:,.0f}")
            
            return productos
        except Exception as e:
            print(f"❌ Error extrayendo productos: {e}")
            return []
    
    def _extraer_datos_producto_mejorado(self, item):
        """Extrae datos de producto - VERSIÓN MEJORADA CON PRECIOS EN PESOS"""
        try:
            # NOMBRE - Búsqueda más exhaustiva
            nombre = "Producto Sin Nombre"
            selectores_nombre = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                '.title', '.nombre', '.name', '.product-title', '.product-name',
                '.titulo', '[class*="title"]', '[class*="nombre"]', '[class*="name"]',
                'strong', 'b', 'span.title', 'a.title'
            ]
            
            for selector in selectores_nombre:
                try:
                    elemento = item.find(selector)
                    if elemento and elemento.get_text(strip=True):
                        texto = elemento.get_text(strip=True)
                        if len(texto) > 3 and len(texto) < 100:  # Filtro de longitud razonable
                            nombre = texto
                            break
                except:
                    continue
            
            # PRECIO EN PESOS - Búsqueda más precisa
            precio_pesos = 0
            texto_completo = item.get_text()
            
            # Patrones más específicos para precios en pesos argentinos
            patrones_precio = [
                r'\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',  # $1.000,00 $ 100.000
                r'\$\s*(\d+(?:\.\d{3})*)',  # $1000 $ 50.000
                r'pesos\s*[\$]?\s*(\d+(?:\.\d{3})*)',  # pesos $1000
                r'precio\s*[\$]?\s*(\d+(?:\.\d{3})*)',  # precio $1000
                r'ARS\s*[\$]?\s*(\d+(?:\.\d{3})*)',  # ARS $1000
                r'(\d+(?:\.\d{3})*)\s*pesos',  # 1000 pesos
            ]
            
            for patron in patrones_precio:
                matches = re.findall(patron, texto_completo, re.IGNORECASE)
                for match in matches:
                    try:
                        # Limpiar el precio: quitar puntos de miles, coma decimal
                        precio_limpio = match.replace('.', '').replace(',', '.')
                        precio_pesos = float(precio_limpio)
                        if precio_pesos > 100:  # Filtro: precio mínimo razonable
                            break
                    except:
                        continue
                if precio_pesos > 0:
                    break
            
            # Si no encuentra con patrones, buscar cualquier número que parezca precio
            if precio_pesos == 0:
                numeros_grandes = re.findall(r'\b(\d{3,}(?:\.\d{3})*)\b', texto_completo)
                for num in numeros_grandes:
                    try:
                        num_limpio = num.replace('.', '')
                        potencial_precio = float(num_limpio)
                        if 1000 <= potencial_precio <= 1000000:  # Rango razonable
                            precio_pesos = potencial_precio
                            break
                    except:
                        continue
            
            # Si todavía no hay precio, descartar el producto
            if precio_pesos == 0:
                return None
            
            # DESCRIPCIÓN - Búsqueda mejorada
            descripcion = f"Producto importado de Zona Litoral: {nombre}"
            selectores_desc = [
                '.description', '.descripcion', '.desc', '.text', '.info',
                'p', 'span', 'div.text', '.product-description', '[class*="desc"]'
            ]
            
            for selector in selectores_desc:
                try:
                    elemento = item.find(selector)
                    if elemento and elemento.get_text(strip=True):
                        texto = elemento.get_text(strip=True)
                        if len(texto) > 20 and len(texto) < 500 and texto != nombre:
                            descripcion = texto
                            break
                except:
                    continue
            
            # IMAGEN - Búsqueda más exhaustiva
            imagen_url = ""
            selectores_imagen = ['img', '[class*="image"]', '[class*="img"]', '.photo', '.foto']
            
            for selector in selectores_imagen:
                try:
                    img_elem = item.find(selector)
                    if img_elem:
                        src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-original') or ""
                        if src:
                            if src.startswith('//'):
                                imagen_url = 'https:' + src
                            elif src.startswith('/'):
                                imagen_url = self.base_url + src
                            elif src.startswith('http'):
                                imagen_url = src
                            break
                except:
                    continue
            
            # CATEGORÍA - Intentar detectar categoría
            categoria = "General"
            # Podemos intentar extraer categoría de la URL o del contexto
            if 'electr' in texto_completo.lower():
                categoria = "Electrónica"
            elif 'hogar' in texto_completo.lower() or 'casa' in texto_completo.lower():
                categoria = "Hogar"
            elif 'deport' in texto_completo.lower():
                categoria = "Deportes"
            elif 'tecno' in texto_completo.lower():
                categoria = "Tecnología"
            elif 'herramienta' in texto_completo.lower():
                categoria = "Herramientas"
            
            # SKU automático mejorado
            from django.utils.crypto import get_random_string
            sku_base = slugify(nombre).upper().replace('-', '')[:12]
            sku = f"ZL-{sku_base}-{get_random_string(4).upper()}"
            
            # CALCULAR PRECIOS EN USD (opcional - puedes mantener solo pesos)
            cotizacion = self.obtener_cotizacion_dolar()
            precio_venta_usd = precio_pesos / cotizacion if cotizacion > 0 else 0
            precio_compra_usd = precio_venta_usd * 0.7  # 30% margen
            
            return {
                'sku': sku,
                'nombre': nombre[:100],
                'descripcion': descripcion[:200],
                'descripcion_larga': descripcion,
                'precio_pesos': precio_pesos,  # ✅ MANTENEMOS PRECIO EN PESOS
                'precio_venta_usd': round(precio_venta_usd, 2),
                'precio_compra_usd': round(precio_compra_usd, 2),
                'stock_actual': 5,
                'stock_minimo': 2,
                'activo': True,
                'publicado_web': True,
                'imagen_url': imagen_url,
                'categoria_web': categoria
            }
        except Exception as e:
            print(f"❌ Error en producto individual: {e}")
            return None

# ✅ IMPORTADOR MASIVO - TODAS LAS CATEGORÍAS AUTOMÁTICAMENTE
class ImportadorMasivo:
    def __init__(self):
        self.base_url = "https://zonalitoral.com.ar"
        self.session = requests.Session()
    
    def obtener_todas_las_categorias(self):
        """Extrae AUTOMÁTICAMENTE todas las categorías de tu sitio"""
        try:
            print("🔍 Buscando todas las categorías...")
            response = self.session.get(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            categorias = []
            
            # Buscar enlaces de categorías en menús
            selectores_menu = [
                'nav a', '.menu a', '.categorias a', 
                '.rubros a', '.product-categories a',
                '[class*="menu"] a', '[class*="categor"] a'
            ]
            
            for selector in selectores_menu:
                enlaces = soup.select(selector)
                for enlace in enlaces:
                    href = enlace.get('href', '')
                    texto = enlace.get_text(strip=True)
                    
                    # Filtrar solo enlaces que parecen categorías de productos
                    if (href and 
                        ('/categoria' in href or '/product-category' in href) and 
                        texto and 
                        len(texto) > 2 and
                        texto not in ['Inicio', 'Contacto', 'Nosotros']):
                        
                        # Completar URL si es relativa
                        if href.startswith('/'):
                            href = self.base_url + href
                        
                        categorias.append({
                            'nombre': texto,
                            'url': href
                        })
                        print(f"✅ Categoría encontrada: {texto}")
            
            # Eliminar duplicados
            categorias_unicas = []
            urls_vistas = set()
            
            for cat in categorias:
                if cat['url'] not in urls_vistas:
                    categorias_unicas.append(cat)
                    urls_vistas.add(cat['url'])
            
            print(f"🎯 Total de categorías únicas: {len(categorias_unicas)}")
            return categorias_unicas
            
        except Exception as e:
            print(f"❌ Error obteniendo categorías: {e}")
            # Si falla, devolver algunas categorías comunes
            return [
                {'nombre': 'Juguetería', 'url': 'https://zonalitoral.com.ar/categoria-producto/jugueteria/'},
                {'nombre': 'Electrónica', 'url': 'https://zonalitoral.com.ar/categoria-producto/electronica/'},
                {'nombre': 'Hogar', 'url': 'https://zonalitoral.com.ar/categoria-producto/hogar/'},
            ]
    
    def importar_todo_el_sitio(self):
        """Importa TODOS los productos de TODAS las categorías"""
        categorias = self.obtener_todas_las_categorias()
        total_productos = 0
        
        for categoria in categorias:
            print(f"\n🔄 Procesando categoría: {categoria['nombre']}")
            
            # Usar el importador simple para esta categoría
            importador_simple = ImportadorWebAutomatico()
            productos_categoria = importador_simple.extraer_productos_desde_url(categoria['url'])
            
            productos_nuevos = 0
            for data in productos_categoria:
                try:
                    # Verificar si ya existe
                    existe = Producto.objects.filter(
                        nombre__iexact=data['nombre'].strip()
                    ).exists()
                    
                    if not existe:
                        # Crear producto con la categoría correcta
                        cat_obj, created = CategoriaProducto.objects.get_or_create(
                            nombre=categoria['nombre'],
                            defaults={'activa': True}
                        )
                        
                        Producto.objects.create(
                            sku=data['sku'],
                            nombre=data['nombre'],
                            descripcion=data['descripcion'],
                            descripcion_larga=data['descripcion_larga'],
                            categoria=cat_obj,
                            precio_compra_usd=data['precio_compra_usd'],
                            precio_venta_usd=data['precio_venta_usd'],
                            stock_actual=data['stock_actual'],
                            stock_minimo=data['stock_minimo'],
                            activo=data['activo'],
                            publicado_web=data['publicado_web'],
                        )
                        
                        productos_nuevos += 1
                        total_productos += 1
                        print(f"✅ {categoria['nombre']}: {data['nombre']}")
                        
                except Exception as e:
                    print(f"❌ Error con producto: {e}")
            
            print(f"✅ {categoria['nombre']}: {productos_nuevos} productos nuevos")
        
        return total_productos

# ✅ VISTA MEJORADA PARA IMPORTACIÓN (CORREGIDA CSRF)
def importar_desde_web_view(request):
    """Vista mejorada para importar productos - MÁS PRODUCTOS + MEJOR DETECCIÓN"""
    importador = ImportadorWebAutomatico()
    productos_importados = []
    
    if request.method == 'POST':
        url = request.POST.get('url', 'https://www.zonalitoral.com.ar')
        
        try:
            # Extraer productos
            productos_data = importador.extraer_productos_desde_url(url)
            
            for data in productos_data:
                try:
                    # Buscar o crear categoría
                    categoria, created_cat = CategoriaProducto.objects.get_or_create(
                        nombre=data.get('categoria_web', 'General'),
                        defaults={'activa': True}
                    )
                    
                    # Crear producto
                    producto, created_prod = Producto.objects.get_or_create(
                        sku=data['sku'],
                        defaults={
                            'nombre': data['nombre'],
                            'descripcion': data['descripcion'],
                            'descripcion_larga': data['descripcion_larga'],
                            'categoria': categoria,
                            'precio_compra_usd': data['precio_compra_usd'],
                            'precio_venta_usd': data['precio_venta_usd'],
                            'stock_actual': data['stock_actual'],
                            'stock_minimo': data['stock_minimo'],
                            'activo': data['activo'],
                            'publicado_web': data['publicado_web'],
                        }
                    )
                    
                    productos_importados.append({
                        'producto': producto,
                        'creado': created_prod,
                        'precio_pesos': data['precio_pesos'],
                        'precio_usd': data['precio_venta_usd'],
                        'imagen_url': data.get('imagen_url', '')
                    })
                    
                except Exception as e:
                    logger.error(f"Error creando producto: {e}")
                    print(f"❌ Error creando producto: {e}")
            
            if productos_importados:
                messages.success(request, f'✅ Importados {len(productos_importados)} productos desde el sitio web')
                messages.info(request, f'📈 Se procesaron más productos con mejor detección de precios')
            else:
                messages.warning(request, '⚠️ No se encontraron productos para importar')
            
        except Exception as e:
            messages.error(request, f'❌ Error importando desde web: {e}')
            print(f"❌ Error general: {e}")
    
    # Obtener token CSRF correctamente
    csrf_token = get_token(request)
    
    # Generar filas de la tabla de productos
    filas_tabla = ""
    for item in productos_importados:
        filas_tabla += f"""
        <tr>
            <td>{item["producto"].nombre}</td>
            <td>{"🆕 CREADO" if item["creado"] else "📝 ACTUALIZADO"}</td>
            <td>${item["precio_pesos"]:,.0f}</td>
            <td>${item["precio_usd"]:,.2f}</td>
            <td>{"✅" if item["imagen_url"] else "❌"}</td>
        </tr>
        """
    
    # Renderizar template simple sin extends
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Importar desde Web - MEJORADO</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .btn {{ background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            .btn:hover {{ background: #218838; }}
            .btn-back {{ background: #6c757d; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; }}
            .btn-back:hover {{ background: #5a6268; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
            th {{ background: #e9ecef; }}
            .mejoras {{ background: #e7f3ff; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Importar Productos desde Web - VERSIÓN MEJORADA</h1>
            
            <div class="mejoras">
                <h3>🆕 MEJORAS INCLUIDAS:</h3>
                <ul>
                    <li>✅ <strong>MÁS PRODUCTOS:</strong> Busca hasta 100 productos (antes 30)</li>
                    <li>✅ <strong>MEJOR DETECCIÓN:</strong> Patrones más precisos para precios en pesos</li>
                    <li>✅ <strong>IMÁGENES:</strong> Búsqueda más exhaustiva de imágenes</li>
                    <li>✅ <strong>CATEGORÍAS:</strong> Detección automática por contenido</li>
                    <li>✅ <strong>PRECIOS EXACTOS:</strong> Mejor conversión de formats argentinos</li>
                </ul>
            </div>

            <div class="card">
                <h3>💡 ¿Cómo funciona?</h3>
                <p>El sistema extraerá automáticamente los productos de tu sitio web</p>
                <p><strong>Novedad:</strong> Ahora busca MÁS productos con MEJOR detección de precios en pesos</p>
            </div>

            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <div style="margin: 15px 0;">
                    <label><strong>URL del sitio web:</strong></label><br>
                    <input type="url" name="url" value="https://www.zonalitoral.com.ar" 
                           style="width: 400px; padding: 8px; margin: 5px 0;">
                </div>
                
                <button type="submit" class="btn">🚀 IMPORTAR PRODUCTOS MEJORADO</button>
            </form>

            {f'''
            <div style="margin: 30px 0;">
                <h3>✅ Productos Importados ({len(productos_importados)})</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th>Estado</th>
                            <th>Precio ARS</th>
                            <th>Precio USD</th>
                            <th>Imagen</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_tabla}
                    </tbody>
                </table>
            </div>
            ''' if productos_importados else ''}

            <div style="margin-top: 40px;">
                <a href="../" class="btn-back">← Volver al listado de productos</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html_content)

# ✅ VISTA MASIVA - IMPORTA TODO EL SITIO (CORREGIDA CSRF)
def importar_todo_el_sitio_view(request):
    """Importa TODAS las categorías y productos AUTOMÁTICAMENTE"""
    if request.method == 'POST':
        importador_masivo = ImportadorMasivo()
        
        try:
            total = importador_masivo.importar_todo_el_sitio()
            messages.success(request, f'🚀 IMPORTACIÓN MASIVA COMPLETADA!')
            messages.success(request, f'📦 Total de productos importados: {total}')
            
        except Exception as e:
            messages.error(request, f'❌ Error en importación masiva: {e}')
    
    # Obtener token CSRF correctamente
    csrf_token = get_token(request)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Importación Masiva</title>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            .btn {{ background: #dc3545; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 18px; }}
            .btn:hover {{ background: #c82333; }}
            .warning {{ background: #fff3cd; padding: 15px; border-radius: 8px; border: 2px solid #ffeaa7; margin: 20px 0; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 IMPORTACIÓN MASIVA</h1>
            
            <div class="warning">
                <h3>⚠️ ADVERTENCIA</h3>
                <p>Esto importará <strong>TODOS los productos de TODAS las categorías</strong> automáticamente.</p>
                <p><strong>Se detectarán automáticamente todas tus categorías</strong></p>
                <p><strong>⏰ Esto puede tomar varios minutos</strong></p>
            </div>

            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <button type="submit" class="btn">🚀 EJECUTAR IMPORTACIÓN MASIVA</button>
            </form>

            <div style="margin-top: 40px;">
                <a href="../" style="background: #6c757d; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">
                    ← Volver al listado de productos
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html_content)

# ✅ RESOURCES PARA IMPORT/EXPORT (MANTENIDOS)
class ProductoResource(resources.ModelResource):
    categoria = fields.Field(
        column_name='categoria',
        attribute='categoria',
        widget=ForeignKeyWidget(CategoriaProducto, 'nombre')
    )
    
    class Meta:
        model = Producto
        skip_unchanged = True
        report_skipped = True
        fields = ('nombre', 'categoria', 'precio_compra_usd', 'precio_venta_usd', 'stock_actual')
        export_order = fields

class CategoriaProductoResource(resources.ModelResource):
    class Meta:
        model = CategoriaProducto
        fields = ('id', 'nombre', 'categoria_padre', 'activa')

# Inline para la galería de imágenes (MANTENIDO)
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 3
    fields = ['imagen', 'titulo', 'orden']

# ✅ PRODUCTO ADMIN (MANTENIDO COMPLETO - CON LA NUEVA URL AGREGADA)
@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin):
    resource_class = ProductoResource
    
    list_display = [
        'nombre', 
        'categoria',
        'precio_venta_usd',
        'stock_actual', 
        'publicado_web',
        'destacado',
        'activo',
    ]
    
    list_display_links = ['nombre']
    
    list_filter = [
        'categoria',
        'activo', 
        'publicado_web',
        'destacado',
        'fecha_creacion'
    ]
    
    search_fields = [
        'nombre', 
        'descripcion', 
        'codigo_barras', 
        'sku',
        'categoria__nombre'
    ]
    
    list_editable = [
        'categoria',
        'precio_venta_usd', 
        'stock_actual',
        'publicado_web',
        'destacado',
        'activo',
    ]
    
    list_per_page = 25
    
    inlines = [ImagenProductoInline]
    
    readonly_fields = [
        'fecha_creacion', 
        'fecha_actualizacion',
    ]
    
    fieldsets = [
        ('📦 INFORMACIÓN BÁSICA', {
            'fields': [
                'nombre',
                'slug',
                'descripcion',
                'descripcion_larga',
                'categoria',
            ],
            'classes': ['wide']
        }),
        
        ('🏷️ INFORMACIÓN TÉCNICA', {
            'fields': [
                'codigo_barras',
                'sku',
            ],
            'classes': ['collapse']
        }),
        
        ('💰 PRECIOS (USD)', {
            'fields': [
                'precio_compra_usd',
                'precio_venta_usd',
            ]
        }),
        
        ('📊 INVENTARIO', {
            'fields': [
                'stock_actual',
                'stock_minimo',
            ]
        }),
        
        ('🖼️ IMAGEN PRINCIPAL', {
            'fields': [
                'imagen_principal',
            ]
        }),
        
        ('🔰 GARANTÍA', {
            'fields': [
                'tiene_garantia',
                'meses_garantia',
                'condiciones_garantia',
                'proveedor_garantia',
            ],
            'classes': ['collapse']
        }),
        
        ('🌐 CONFIGURACIÓN WEB', {
            'fields': [
                'publicado_web',
                'destacado',
                'orden_destacado',
                'tags',
            ]
        }),
        
        ('🔍 SEO', {
            'fields': [
                'meta_titulo',
                'meta_descripcion',
            ],
            'classes': ['collapse']
        }),
        
        ('📅 AUDITORÍA', {
            'fields': [
                'activo',
                'fecha_creacion',
                'fecha_actualizacion',
            ],
            'classes': ['collapse']
        }),
    ]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('importar-desde-web/', 
                 self.admin_site.admin_view(importar_desde_web_view),
                 name='importar_desde_web'),
            # ✅ AGREGÁ ESTA LÍNEA NUEVA:
            path('importar-todo/', 
                 self.admin_site.admin_view(importar_todo_el_sitio_view),
                 name='importar_todo_el_sitio'),
        ]
        return custom_urls + urls

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.nombre)
        
        condiciones_por_meses = {
            3: "🔰 GARANTÍA BÁSICA - 3 MESES",
            6: "🔰 GARANTÍA ESTÁNDAR - 6 MESES", 
            12: "🔰 GARANTÍA EXTENDIDA - 12 MESES"
        }
        
        if obj.tiene_garantia and obj.meses_garantia in condiciones_por_meses:
            obj.condiciones_garantia = condiciones_por_meses[obj.meses_garantia]
        else:
            obj.condiciones_garantia = "Producto sin garantía"
            obj.meses_garantia = 0
        
        obj.proveedor_garantia = "Zona Litoral - Garantía Oficial"
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Valores por defecto
        form.base_fields['meses_garantia'].initial = 12
        form.base_fields['tiene_garantia'].initial = True
        form.base_fields['activo'].initial = True
        form.base_fields['publicado_web'].initial = True
        form.base_fields['stock_actual'].initial = 0
        form.base_fields['stock_minimo'].initial = 5
        
        return form

# ✅ CATEGORÍA ADMIN (MANTENIDO COMPLETO)
@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(ImportExportModelAdmin):
    resource_class = CategoriaProductoResource
    
    list_display = ['nombre', 'categoria_padre', 'activa', 'fecha_creacion']
    list_filter = ['categoria_padre', 'activa', 'fecha_creacion']
    search_fields = ['nombre']
    list_editable = ['activa']
    prepopulated_fields = {"slug": ("nombre",)}

# Registrar solo los modelos necesarios
admin.site.register(CotizacionDolar)