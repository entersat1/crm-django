<<<<<<< HEAD
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Producto, CategoriaProducto  # ✅ CORREGIDO: Importar CategoriaProducto

def catalogo_web(request):
    """Catálogo público de productos"""
    productos = Producto.objects.filter(
        publicado_web=True, 
        activo=True
    ).order_by('-orden_destacado', 'nombre')
    
    # Filtros
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria__nombre__icontains=categoria)
    
    garantia = request.GET.get('garantia')
    if garantia == 'con':
        productos = productos.filter(tiene_garantia=True)
    
    context = {
        'productos': productos,
        'categorias': CategoriaProducto.objects.all(),  # ✅ CORREGIDO: CategoriaProducto
        'total_productos': productos.count()
    }
    return render(request, 'web/catalogo.html', context)

def detalle_producto_web(request, slug):
    """Página individual de producto"""
    producto = get_object_or_404(Producto, slug=slug, publicado_web=True)
    
    # Productos relacionados (misma categoría)
    relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        publicado_web=True,
        activo=True
    ).exclude(id=producto.id)[:4]
    
    context = {
        'producto': producto,
        'relacionados': relacionados,
        'garantia_info': producto.garantia_info
    }
=======
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Producto, CategoriaProducto  # ✅ CORREGIDO: Importar CategoriaProducto

def catalogo_web(request):
    """Catálogo público de productos"""
    productos = Producto.objects.filter(
        publicado_web=True, 
        activo=True
    ).order_by('-orden_destacado', 'nombre')
    
    # Filtros
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria__nombre__icontains=categoria)
    
    garantia = request.GET.get('garantia')
    if garantia == 'con':
        productos = productos.filter(tiene_garantia=True)
    
    context = {
        'productos': productos,
        'categorias': CategoriaProducto.objects.all(),  # ✅ CORREGIDO: CategoriaProducto
        'total_productos': productos.count()
    }
    return render(request, 'web/catalogo.html', context)

def detalle_producto_web(request, slug):
    """Página individual de producto"""
    producto = get_object_or_404(Producto, slug=slug, publicado_web=True)
    
    # Productos relacionados (misma categoría)
    relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        publicado_web=True,
        activo=True
    ).exclude(id=producto.id)[:4]
    
    context = {
        'producto': producto,
        'relacionados': relacionados,
        'garantia_info': producto.garantia_info
    }
>>>>>>> 221a76dd27c1c9ad53cabb1d52123a32be198d53
    return render(request, 'web/detalle_producto.html', context)