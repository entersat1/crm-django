import os
import subprocess
import sys

def crear_archivo(ruta, contenido=""):
    """Crear archivo con contenido"""
    directorio = os.path.dirname(ruta)
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    
    with open(ruta, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"✓ Creado: {ruta}")

# Crear estructura
apps = ['core', 'clientes', 'inventario', 'servicios']

for app in apps:
    if os.path.exists(app):
        # __init__.py principal
        crear_archivo(os.path.join(app, '__init__.py'))
        
        # Migrations
        migrations_dir = os.path.join(app, 'migrations')
        crear_archivo(os.path.join(migrations_dir, '__init__.py'))

# Crear modelos
modelos = {
    'clientes': '''
from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.nombre
''',
    
    'inventario': '''
from django.db import models

class Equipo(models.Model):
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.marca} {self.modelo}"
''',
    
    'servicios': '''
from django.db import models

class OrdenTaller(models.Model):
    numero = models.CharField(max_length=20)
    
    def __str__(self):
        return self.numero
'''
}

for app, modelo in modelos.items():
    if os.path.exists(app):
        crear_archivo(os.path.join(app, 'models.py'), modelo.strip())

print("✓ Estructura creada. Ejecuta: python manage.py runserver")