from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
import io
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # 🔥 CORREGIDO: Campos básicos que probablemente existen
    list_display = ['id', 'nombre']  # Solo campos seguros
    
    # 🔥 CORREGIDO: search_fields REQUERIDO
    search_fields = ['nombre']  # Campo básico que debería existir
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('importar-csv/', self.importar_archivo, name='importar_csv'),
        ]
        return custom_urls + urls
    
    def importar_archivo(self, request):
        if request.method == 'POST':
            archivo = request.FILES['csv_file']
            
            if not archivo.name.endswith(('.csv', '.xlsx', '.xls')):
                messages.error(request, '❌ Formato no soportado. Use CSV o Excel (.xlsx, .xls)')
                return redirect('..')
            
            try:
                productos_importados = 0
                
                # LEER ARCHIVO
                if archivo.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(archivo)
                else:
                    df = pd.read_csv(archivo)
                
                print(f"🔍 Columnas en el archivo: {list(df.columns)}")
                
                # Buscar columna de nombres
                columna_nombre = None
                for col in df.columns:
                    if any(palabra in col.lower() for palabra in ['nombre', 'name', 'producto', 'product']):
                        columna_nombre = col
                        break
                
                if not columna_nombre and len(df.columns) > 0:
                    columna_nombre = df.columns[0]  # Usar primera columna
                
                if not columna_nombre:
                    messages.error(request, '❌ No se encontró columna de nombres')
                    return redirect('..')
                
                # PROCESAR CADA FILA
                for index, row in df.iterrows():
                    try:
                        nombre = str(row[columna_nombre]).strip()
                        if not nombre or nombre.lower() in ['nan', 'none', '']:
                            continue
                        
                        # Crear producto básico
                        producto, created = Producto.objects.get_or_create(
                            nombre=nombre,
                            defaults={'nombre': nombre}
                        )
                        
                        if created:
                            productos_importados += 1
                            print(f"✅ NUEVO: {nombre}")
                    
                    except Exception as e:
                        print(f"❌ Error en fila {index}: {e}")
                        continue
                
                if productos_importados > 0:
                    messages.success(request, f'✅ Importación exitosa! Nuevos: {productos_importados}')
                else:
                    messages.warning(request, '⚠️ No se importaron productos nuevos')
                
            except Exception as e:
                messages.error(request, f'❌ Error al importar: {str(e)}')
        
        return render(request, 'admin/csv_form.html')