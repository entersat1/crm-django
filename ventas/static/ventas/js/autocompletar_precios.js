// ventas/static/ventas/js/autocompletar_precios.js
document.addEventListener('DOMContentLoaded', function() {
    console.log(' Script de autocompletado de precios cargado');
    
    // Función para obtener el precio de un producto
    function obtenerPrecioProducto(productoId) {
        return fetch('/api/productos/' + productoId + '/precio/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Producto no encontrado');
                }
                return response.json();
            })
            .then(data => {
                return data.precio_venta_usd;
            })
            .catch(error => {
                console.error('Error obteniendo precio:', error);
                return 0;
            });
    }
    
    // Escuchar cambios en los selects de producto
    document.addEventListener('change', function(e) {
        if (e.target && e.target.matches('select[id*=\"producto\"]')) {
            var productoId = e.target.value;
            var row = e.target.closest('.form-row');
            
            console.log('Producto seleccionado:', productoId);
            
            if (productoId && row) {
                // Obtener el campo de precio
                var precioField = row.querySelector('input[id*=\"precio_unitario\"]');
                
                if (precioField) {
                    console.log('Campo de precio encontrado');
                    // Obtener y asignar el precio
                    obtenerPrecioProducto(productoId).then(function(precio) {
                        if (precio > 0) {
                            precioField.value = precio;
                            console.log('Precio asignado:', precio);
                            
                            // Disparar evento change para recalcular subtotales
                            var event = new Event('change', { bubbles: true });
                            precioField.dispatchEvent(event);
                        }
                    });
                }
            }
        }
    });
});
