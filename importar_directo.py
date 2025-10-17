import os
import pandas as pd
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Producto

def importar_directo(archivo_path):
    print(f"🚀 IMPORTACIÓN DIRECTA DESDE: {archivo_path}")
    
    if archivo_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(archivo_path)
    else:
        df = pd.read_csv(archivo_path)
    
    print(f"📊 Filas: {len(df)}, Columnas: {list(df.columns)}")
    
    for index, row in df.iterrows():
        try:
            # Tomar el primer campo no vacío como nombre
            nombre = None
            for col in df.columns:
                if pd.notna(row[col]) and str(row[col]).strip():
                    nombre = str(row[col]).strip()[:100]
                    break
            
            if not nombre:
                nombre = f"Producto {index + 1}"
            
            # Buscar algún número que pueda ser precio
            precio = 0
            for col in df.columns:
                if pd.notna(row[col]):
                    try:
                        valor = str(row[col])
                        # Si parece un precio (tiene números)
                        if any(c.isdigit() for c in valor) and len(valor) < 20:
                            # Extraer números
                            numeros = ''.join(c for c in valor if c.isdigit() or c == '.')
                            if numeros and '.' in numeros:
                                temp_precio = float(numeros)
                                if 1 < temp_precio < 1000000:  # Precio razonable
                                    precio = temp_precio
                                    break
                    except:
                        continue
            
            # CREAR SI O SI
            producto, created = Producto.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': f"Importado: {nombre}",
                    'precio': precio,
                    'stock': 10,
                    'categoria': 'Direct Import',
                    'activo': True
                }
            )
            
            if created:
                print(f"✅ {index+1:3d}. {nombre} - ${precio}")
            else:
                print(f"📦 {index+1:3d}. YA EXISTE: {nombre}")
                
        except Exception as e:
            print(f"❌ {index+1:3d}. ERROR: {e}")
    
    print(f"🎉 TOTAL PRODUCTOS EN SISTEMA: {Producto.objects.count()}")

# Ejecutar si hay archivos en la carpeta
archivos = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx', '.xls'))]
if archivos:
    importar_directo(archivos[0])
else:
    print("❌ No hay archivos CSV o Excel en la carpeta")
    print("💡 Coloca tu archivo en C:\mi_sistema\ y ejecuta de nuevo")