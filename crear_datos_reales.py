<<<<<<< HEAD
# crear_datos_reales.py
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_sistema.settings')
django.setup()

from clientes.models import Cliente
from inventario.models import Producto, CategoriaProducto
from servicios.models import OrdenTaller, ProductoUtilizado

print("🧹 Limpiando datos existentes...")
ProductoUtilizado.objects.all().delete()
OrdenTaller.objects.all().delete()

print("📦 Creando categorías...")
categoria_electronica, _ = CategoriaProducto.objects.get_or_create(nombre="Electrónicos")
categoria_software, _ = CategoriaProducto.objects.get_or_create(nombre="Software")

print("👥 Creando clientes...")
cliente1 = Cliente.objects.create(
    nombre="Carlos Mendoza", 
    email="carlos@zonalitoral.com", 
    telefono="291-1234567"
)
cliente2 = Cliente.objects.create(
    nombre="Ana Bustos", 
    email="ana@empresa.com", 
    telefono="291-9876543"
)

print("🛍️ Creando productos...")
producto1 = Producto.objects.create(
    nombre="Disco SSD 500GB", 
    precio=85.00, 
    stock=10, 
    categoria=categoria_electronica
)
producto2 = Producto.objects.create(
    nombre="Memoria RAM 8GB", 
    precio=45.00, 
    stock=5, 
    categoria=categoria_electronica
)
producto3 = Producto.objects.create(
    nombre="Licencia Windows 11", 
    precio=120.00, 
    stock=8, 
    categoria=categoria_software
)

print("🔧 Creando órdenes de taller...")
orden1 = OrdenTaller.objects.create(
    cliente=cliente1,
    equipo="Laptop HP Pavilion 15",
    problema="No enciende, hace sonidos de beep",
    diagnostico="Memoria RAM defectuosa y disco dañado",
    solucion="Reemplazo de memoria RAM y instalación de SSD nuevo",
    estado="completado",
    prioridad="urgente",
    tecnico_asignado="Juan Pérez",
    costo_mano_obra=150.00,
    numero_orden="OT-2024-001"
)

print("➕ Agregando productos a la orden 1...")
orden1.agregar_producto(producto2, 1, 45.00)  # RAM
orden1.agregar_producto(producto1, 1, 85.00)  # SSD

orden2 = OrdenTaller.objects.create(
    cliente=cliente2,
    equipo="PC Desktop Gamer",
    problema="Sobrecalentamiento y reinicios",
    diagnostico="Ventiladores obstruidos y sistema operativo corrupto",
    solucion="Limpieza interna y reinstalación de Windows",
    estado="reparacion",
    prioridad="alta",
    tecnico_asignado="María González",
    costo_mano_obra=200.00,
    numero_orden="OT-2024-002"
)

print("➕ Agregando productos a la orden 2...")
orden2.agregar_producto(producto3, 1, 120.00)  # Windows

print("\n✅ DATOS CREADOS EXITOSAMENTE:")
print(f"👥 Clientes: {Cliente.objects.count()}")
print(f"📦 Productos: {Producto.objects.count()}")
print(f"🔧 Órdenes: {OrdenTaller.objects.count()}")
print(f"🛒 Productos utilizados: {ProductoUtilizado.objects.count()}")

print("\n💰 TOTALES DE ÓRDENES:")
for orden in OrdenTaller.objects.all():
    total = orden.calcular_total()
    print(f"Orden #{orden.numero_orden}: ${total} (Mano obra: ${orden.costo_mano_obra} + Repuestos: ${orden.costo_repuestos})")

=======
# crear_datos_reales.py
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_sistema.settings')
django.setup()

from clientes.models import Cliente
from inventario.models import Producto, CategoriaProducto
from servicios.models import OrdenTaller, ProductoUtilizado

print("🧹 Limpiando datos existentes...")
ProductoUtilizado.objects.all().delete()
OrdenTaller.objects.all().delete()

print("📦 Creando categorías...")
categoria_electronica, _ = CategoriaProducto.objects.get_or_create(nombre="Electrónicos")
categoria_software, _ = CategoriaProducto.objects.get_or_create(nombre="Software")

print("👥 Creando clientes...")
cliente1 = Cliente.objects.create(
    nombre="Carlos Mendoza", 
    email="carlos@zonalitoral.com", 
    telefono="291-1234567"
)
cliente2 = Cliente.objects.create(
    nombre="Ana Bustos", 
    email="ana@empresa.com", 
    telefono="291-9876543"
)

print("🛍️ Creando productos...")
producto1 = Producto.objects.create(
    nombre="Disco SSD 500GB", 
    precio=85.00, 
    stock=10, 
    categoria=categoria_electronica
)
producto2 = Producto.objects.create(
    nombre="Memoria RAM 8GB", 
    precio=45.00, 
    stock=5, 
    categoria=categoria_electronica
)
producto3 = Producto.objects.create(
    nombre="Licencia Windows 11", 
    precio=120.00, 
    stock=8, 
    categoria=categoria_software
)

print("🔧 Creando órdenes de taller...")
orden1 = OrdenTaller.objects.create(
    cliente=cliente1,
    equipo="Laptop HP Pavilion 15",
    problema="No enciende, hace sonidos de beep",
    diagnostico="Memoria RAM defectuosa y disco dañado",
    solucion="Reemplazo de memoria RAM y instalación de SSD nuevo",
    estado="completado",
    prioridad="urgente",
    tecnico_asignado="Juan Pérez",
    costo_mano_obra=150.00,
    numero_orden="OT-2024-001"
)

print("➕ Agregando productos a la orden 1...")
orden1.agregar_producto(producto2, 1, 45.00)  # RAM
orden1.agregar_producto(producto1, 1, 85.00)  # SSD

orden2 = OrdenTaller.objects.create(
    cliente=cliente2,
    equipo="PC Desktop Gamer",
    problema="Sobrecalentamiento y reinicios",
    diagnostico="Ventiladores obstruidos y sistema operativo corrupto",
    solucion="Limpieza interna y reinstalación de Windows",
    estado="reparacion",
    prioridad="alta",
    tecnico_asignado="María González",
    costo_mano_obra=200.00,
    numero_orden="OT-2024-002"
)

print("➕ Agregando productos a la orden 2...")
orden2.agregar_producto(producto3, 1, 120.00)  # Windows

print("\n✅ DATOS CREADOS EXITOSAMENTE:")
print(f"👥 Clientes: {Cliente.objects.count()}")
print(f"📦 Productos: {Producto.objects.count()}")
print(f"🔧 Órdenes: {OrdenTaller.objects.count()}")
print(f"🛒 Productos utilizados: {ProductoUtilizado.objects.count()}")

print("\n💰 TOTALES DE ÓRDENES:")
for orden in OrdenTaller.objects.all():
    total = orden.calcular_total()
    print(f"Orden #{orden.numero_orden}: ${total} (Mano obra: ${orden.costo_mano_obra} + Repuestos: ${orden.costo_repuestos})")

>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
print("\n🎯 ¡Datos listos para facturación!")