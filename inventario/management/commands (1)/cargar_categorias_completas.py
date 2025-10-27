<<<<<<< HEAD
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from inventario.models import CategoriaProducto

class Command(BaseCommand):
    help = 'Cargar todas las categorías y subcategorías del sistema Zona Litoral'
    
    def handle(self, *args, **options):
        
        categorias_data = {
            # CATEGORÍAS PRINCIPALES CON SUS SUBCATEGORÍAS
            "Jugueteria": [],
            
            "Articulos Oficina y Libreria": [
                "CARPETAS", "Goma de borrar", "Cartucheras", "Separadores hojas",
                "Sacapuntas y guillotinas", "PINCELES", "Cuadernos Y Agendas",
                "Cuadernos y Hojas", "Banderitas Señaladoras Sticky Notes",
                "Chinches, ganchos, banditas", "Abrochadora", "Pegamentos y plasticolas",
                "Escritura", "Kit o set de Escritura", "Lapices", "Fibras, Fibrones",
                "Biromes y repuestos", "Cintas adhesivas"
            ],
            
            "Todo para el mate": [
                "Termos", "Botellas agua y otros", "Yerbas", "Bolsos materos",
                "Mates y bombillas", "Tapas termos", "Pavas"
            ],
            
            "Auriculares": [
                "Auriculares intraurales con cable", "Auriculares Intraurales inalambricos",
                "Auriculares intraurales gamer", "Auriculares Vincha con cable",
                "Auriculares vincha Gamer", "Auriculares vincha inalambricos",
                "Soporte auriculares"
            ],
            
            "Teclados y Mouses": [
                "Pad Mouse", "Combo teclado y mouse gamer", "Mouse", "Teclados",
                "Teclado y mouse", "Teclados Gamers"
            ],
            
            "Seguridad": [],
            "Webcam": [],
            "Microfonos": [],
            
            "Red": [
                "Modem y router", "Placa Red", "Repetidores y Antenas"
            ],
            
            "Parlantes": [],
            
            "Notebook y accesorios": [
                "Notebook", "Cargadores", "Bases refrigeracion"
            ],
            
            "Conectividad IR y Bluetooth": [],
            
            "Impresoras e insumos": [
                "Cable impresora", "Cartuchos HP alt", "Impresoras Laser", "Toner Alt",
                "Unidad de imagen", "Cartucho HP orig", "Tintas", "Cartucho epson Alt"
            ],
            
            "Papelería": [],
            "Pendrive y memorias": [],
            "Pilas y Baterias": [],
            
            "Computadoras": [
                "Placas de sonido", "Carry disk", "Cooler y ventiladores", "Memorias",
                "Placas Madres", "Micro", "Grabadoras Lectoras", "Fuentes pc",
                "Gabinetes", "Discos ssd/hd"
            ],
            
            "Herramientas": [],
            "Mochilas, bolsos y fundas": [],
            "Joystick": [],
            "Consolas Juegos": [],
            "Smartwatch": [],
            "Puertos y Hub USB": [],
            "UPS y Estabilizador": [],
            "Adaptadores y Conversores": [],
            "Soportes TV y monitor": [],
            "Iluminacion y electricidad": [],
            "Tripodes": [],
            "Tabletas Digitales": [],
            
            "Celulares": [
                "Cargadores celular"
            ],
            
            "TV BOX": [],
            "Sillas y Muebles": [],
            
            "Cables y adaptadores": [
                "Cables red", "Cables y adaptadores de sonido", 
                "Cables video", "Cable celulares"
            ],
            
            "Tecnologia y Computacion": []
        }
        
        total_creadas = 0
        
        for categoria_principal, subcategorias in categorias_data.items():
            # Crear categoría principal
            cat_principal, created = CategoriaProducto.objects.get_or_create(
                nombre=categoria_principal,
                categoria_padre=None,
                defaults={'slug': slugify(categoria_principal)}
            )
            if created:
                total_creadas += 1
                self.stdout.write(f"✅ Categoría principal: {categoria_principal}")
            
            # Crear subcategorías
            for subcategoria_nombre in subcategorias:
                subcat, created = CategoriaProducto.objects.get_or_create(
                    nombre=subcategoria_nombre,
                    categoria_padre=cat_principal,
                    defaults={'slug': slugify(subcategoria_nombre)}
                )
                if created:
                    total_creadas += 1
                    self.stdout.write(f"   📂 Subcategoría: {subcategoria_nombre}")
        
        self.stdout.write(
            self.style.SUCCESS(f'🎉 ¡Sistema de categorías cargado! Total: {total_creadas} categorías')
=======
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from inventario.models import CategoriaProducto

class Command(BaseCommand):
    help = 'Cargar todas las categorías y subcategorías del sistema Zona Litoral'
    
    def handle(self, *args, **options):
        
        categorias_data = {
            # CATEGORÍAS PRINCIPALES CON SUS SUBCATEGORÍAS
            "Jugueteria": [],
            
            "Articulos Oficina y Libreria": [
                "CARPETAS", "Goma de borrar", "Cartucheras", "Separadores hojas",
                "Sacapuntas y guillotinas", "PINCELES", "Cuadernos Y Agendas",
                "Cuadernos y Hojas", "Banderitas Señaladoras Sticky Notes",
                "Chinches, ganchos, banditas", "Abrochadora", "Pegamentos y plasticolas",
                "Escritura", "Kit o set de Escritura", "Lapices", "Fibras, Fibrones",
                "Biromes y repuestos", "Cintas adhesivas"
            ],
            
            "Todo para el mate": [
                "Termos", "Botellas agua y otros", "Yerbas", "Bolsos materos",
                "Mates y bombillas", "Tapas termos", "Pavas"
            ],
            
            "Auriculares": [
                "Auriculares intraurales con cable", "Auriculares Intraurales inalambricos",
                "Auriculares intraurales gamer", "Auriculares Vincha con cable",
                "Auriculares vincha Gamer", "Auriculares vincha inalambricos",
                "Soporte auriculares"
            ],
            
            "Teclados y Mouses": [
                "Pad Mouse", "Combo teclado y mouse gamer", "Mouse", "Teclados",
                "Teclado y mouse", "Teclados Gamers"
            ],
            
            "Seguridad": [],
            "Webcam": [],
            "Microfonos": [],
            
            "Red": [
                "Modem y router", "Placa Red", "Repetidores y Antenas"
            ],
            
            "Parlantes": [],
            
            "Notebook y accesorios": [
                "Notebook", "Cargadores", "Bases refrigeracion"
            ],
            
            "Conectividad IR y Bluetooth": [],
            
            "Impresoras e insumos": [
                "Cable impresora", "Cartuchos HP alt", "Impresoras Laser", "Toner Alt",
                "Unidad de imagen", "Cartucho HP orig", "Tintas", "Cartucho epson Alt"
            ],
            
            "Papelería": [],
            "Pendrive y memorias": [],
            "Pilas y Baterias": [],
            
            "Computadoras": [
                "Placas de sonido", "Carry disk", "Cooler y ventiladores", "Memorias",
                "Placas Madres", "Micro", "Grabadoras Lectoras", "Fuentes pc",
                "Gabinetes", "Discos ssd/hd"
            ],
            
            "Herramientas": [],
            "Mochilas, bolsos y fundas": [],
            "Joystick": [],
            "Consolas Juegos": [],
            "Smartwatch": [],
            "Puertos y Hub USB": [],
            "UPS y Estabilizador": [],
            "Adaptadores y Conversores": [],
            "Soportes TV y monitor": [],
            "Iluminacion y electricidad": [],
            "Tripodes": [],
            "Tabletas Digitales": [],
            
            "Celulares": [
                "Cargadores celular"
            ],
            
            "TV BOX": [],
            "Sillas y Muebles": [],
            
            "Cables y adaptadores": [
                "Cables red", "Cables y adaptadores de sonido", 
                "Cables video", "Cable celulares"
            ],
            
            "Tecnologia y Computacion": []
        }
        
        total_creadas = 0
        
        for categoria_principal, subcategorias in categorias_data.items():
            # Crear categoría principal
            cat_principal, created = CategoriaProducto.objects.get_or_create(
                nombre=categoria_principal,
                categoria_padre=None,
                defaults={'slug': slugify(categoria_principal)}
            )
            if created:
                total_creadas += 1
                self.stdout.write(f"✅ Categoría principal: {categoria_principal}")
            
            # Crear subcategorías
            for subcategoria_nombre in subcategorias:
                subcat, created = CategoriaProducto.objects.get_or_create(
                    nombre=subcategoria_nombre,
                    categoria_padre=cat_principal,
                    defaults={'slug': slugify(subcategoria_nombre)}
                )
                if created:
                    total_creadas += 1
                    self.stdout.write(f"   📂 Subcategoría: {subcategoria_nombre}")
        
        self.stdout.write(
            self.style.SUCCESS(f'🎉 ¡Sistema de categorías cargado! Total: {total_creadas} categorías')
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
        )