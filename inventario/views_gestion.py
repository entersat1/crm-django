from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
import json
from .models import Producto

@staff_member_required
def sistema_gestion_productos(request):
    """Sistema completo de gestión de productos - HTML DIRECTO"""
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Gestión - Zona Litoral</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
            body { background: #f5f5f5; padding: 20px; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .container { display: flex; gap: 20px; flex-wrap: wrap; }
            .panel { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex: 1; min-width: 300px; }
            .panel h3 { margin-bottom: 15px; color: #2c3e50; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; font-size: 16px; width: 100%; }
            button:hover { background: #0056b3; }
            .actions { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
            .action-btn { display: block; padding: 12px; text-align: center; text-decoration: none; border-radius: 3px; font-weight: bold; }
            .btn-warning { background: #ffc107; color: #212529; }
            .btn-secondary { background: #6c757d; color: white; }
            .btn-success { background: #28a745; color: white; }
            .info-box { background: #f8f9fa; padding: 15px; border-radius: 3px; border-left: 4px solid #007bff; }
            .info-box h4 { margin-bottom: 10px; color: #2c3e50; }
            .info-box ul { padding-left: 20px; }
            .info-box li { margin-bottom: 5px; color: #666; }
            @media (max-width: 768px) { .container { flex-direction: column; } }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏪 Sistema de Gestión - Zona Litoral</h1>
            <p>Subdominio: sistema.zonalitoral.com.ar</p>
        </div>

        <div class="container">
            <div class="panel">
                <h3>📦 Gestión Manual de Productos</h3>
                <form id="form-producto">
                    <div class="form-group">
                        <label for="nombre-producto">Nombre del Producto *</label>
                        <input type="text" id="nombre-producto" required>
                    </div>
                    <div class="form-group">
                        <label for="precio-producto">Precio USD *</label>
                        <input type="number" step="0.01" id="precio-producto" required>
                    </div>
                    <div class="form-group">
                        <label for="categoria-producto">Categoría</label>
                        <select id="categoria-producto">
                            <option value="Jugueteria">Jugueteria</option>
                            <option value="Articulos Oficina y Libreria">Artículos Oficina y Librería</option>
                            <option value="Todo para el mate">Todo para el mate</option>
                            <option value="Auriculares">Auriculares</option>
                            <option value="Teclados y Mouses">Teclados y Mouses</option>
                            <option value="Tecnologia y Computacion">Tecnología y Computación</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="descripcion-producto">Descripción</label>
                        <textarea id="descripcion-producto" rows="3" placeholder="Descripción del producto..."></textarea>
                    </div>
                    <button type="submit">Agregar Producto</button>
                </form>
            </div>

            <div class="panel">
                <h3>🚀 Acciones Rápidas</h3>
                <div class="actions">
                    <a href="/admin/inventario/producto/" class="action-btn btn-warning" target="_blank">⚙️ Admin Productos (CSV)</a>
                    <a href="/admin/" class="action-btn btn-secondary" target="_blank">🔧 Admin General</a>
                    <a href="/" class="action-btn btn-success" target="_blank">👀 Ver Sitio Web</a>
                </div>
                <div class="info-box">
                    <h4>📋 Información del Sistema</h4>
                    <p><strong>Campos automáticos:</strong></p>
                    <ul>
                        <li>Stock inicial: 10 unidades</li>
                        <li>Stock mínimo: 5 unidades</li>
                        <li>Código de barras: Generado automáticamente</li>
                        <li>Estado: Activo</li>
                    </ul>
                </div>
            </div>
        </div>

        <script>
        document.getElementById('form-producto').addEventListener('submit', function(e) {
            e.preventDefault();
            const nombre = document.getElementById('nombre-producto').value;
            const precio = document.getElementById('precio-producto').value;
            const categoria = document.getElementById('categoria-producto').value;
            const descripcion = document.getElementById('descripcion-producto').value;
            
            if (!nombre) { alert('❌ El nombre del producto es obligatorio'); return; }
            if (!precio || precio <= 0) { alert('❌ El precio debe ser mayor a 0'); return; }
            
            const formData = {
                action: 'agregar_producto',
                nombre: nombre,
                precio: parseFloat(precio),
                categoria: categoria,
                descripcion: descripcion || 'Producto: ' + nombre
            };
            
            fetch('/sistema/inventario/api/gestion-productos/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('✅ ' + data.message + '\\n📦 Código: ' + data.codigo_barras);
                    document.getElementById('form-producto').reset();
                } else {
                    alert('❌ Error: ' + data.message);
                }
            })
            .catch(error => {
                alert('❌ Error de conexión: ' + error);
            });
        });

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        </script>
    </body>
    </html>
    """
    
    return HttpResponse(html_content)

@staff_member_required
def api_gestion_productos(request):
    """API para el sistema de gestión"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'agregar_producto':
                # Procesar nuevo producto
                nombre = data.get('nombre', '').strip()
                precio = float(data.get('precio', 0))
                categoria = data.get('categoria', 'General')
                descripcion = data.get('descripcion', f'Producto: {nombre}')
                
                if nombre:
                    # 🎯 USANDO TUS CAMPOS REALES
                    producto = Producto(
                        nombre=nombre,
                        precio_venta_usd=precio,
                        categoria=categoria,
                        descripcion=descripcion,
                        stock_actual=10,
                        stock_minimo=5,
                        activo=True,
                        codigo_barras=f"ZL{Producto.objects.count() + 1:06d}"
                    )
                    producto.save()
                    
                    return JsonResponse({
                        'status': 'success', 
                        'message': f'Producto "{nombre}" agregado correctamente',
                        'id': producto.id,
                        'codigo_barras': producto.codigo_barras
                    })
                else:
                    return JsonResponse({'status': 'error', 'message': 'Nombre requerido'})
            
            return JsonResponse({'status': 'error', 'message': 'Acción no válida'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})