from django.contrib import admin
from .models import CategoriaProducto, Producto, MovimientoStock

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio_venta', 'stock_actual', 'stock_minimo', 'stock_bajo', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre']

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'stock_nuevo', 'referencia', 'fecha']
    list_filter = ['tipo', 'fecha']
    readonly_fields = ['fecha']
