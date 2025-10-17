import os
import pandas as pd
import re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Producto

def limpiar_para_consola(texto):
    """Eliminar caracteres que causan problemas en consola Windows"""
    if pd.isna(texto):
        return ""
    
    texto_str = str(texto)
    # Solo mantener caracteres ASCII básicos y letras con acento
    texto_limpio = ''.join(
        c for c in texto_str 
        if ord(c) < 127 or c in 'áéíóúñÁÉÍÓÚÑ'
    )
    return texto_limpio.strip()

def importar_desde_archivo(archivo_path):
    print(f"IMPORTANDO DESDE: {archivo_path}")
    
    try:
        if archivo_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(archivo_path)
        else:
            df = pd.read_csv(archivo_path, encoding='utf-8')
    except:
        try:
            df = pd.read_csv(archivo_path, encoding='latin-1')
        except:
            df = pd.read_csv(archivo_path, encoding='cp1252')
    
    print(f"FILAS: {len(df)}")
    print(f"COLUMNAS: {list(df.columns)}")
    
    importados = 0
    
    for index, row in df.iterrows():
        try:
            # Usar primera columna como nombre
            primera_col = df.columns[0]
            nombre = limpiar_para_consola(row[primera_col])
            
            if not nombre or nombre.lower() in ['nan', 'none', '']:
                nombre = f"Producto {index + 1}"
            
            # Buscar precio en cualquier columna
            precio = 0
            for col in df.columns:
                if pd.notna(row[col]):
                    try:
                        texto = str(row[col])
                        # Buscar números
                        numeros = re.findall(r'\d+\.?\d*', texto)
                        if numeros:
                            posible_precio = float(numeros[0])
                            if 1 < posible_precio < 1000000:
                                precio = posible_precio
                                break
                    except:
                        continue
            
            # CREAR
            producto, created = Producto.objects.get_or_create(
                nombre=nombre[:100],
                defaults={
                    'descripcion': f"Importado: {nombre}",
                    'precio': precio,
                    'stock': 10,
                    'categoria': 'Consola Import',
                    'activo': True
                }
            )
            
            if created:
                importados += 1
                print(f"{index+1:3d}. {nombre} - ${precio}")
                
        except Exception as e:
            print(f"ERROR {index+1}: {str(e)}")
    
    print(f"IMPORTADOS: {importados}")
    print(f"TOTAL SISTEMA: {Producto.objects.count()}")

# Buscar archivos y importar
archivos = [f for f in os.listdir('.') if f.endswith(('.csv', '.xlsx', '.xls'))]
if archivos:
    importar_desde_archivo(archivos[0])
else:
    print("No hay archivos para importar")