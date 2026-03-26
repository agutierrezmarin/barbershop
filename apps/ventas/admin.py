from django.contrib import admin
from .models import Venta, ItemVenta, CorteCaja

class ItemVentaInline(admin.TabularInline):
    model = ItemVenta
    extra = 1
    readonly_fields = ['subtotal']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['pk', 'cliente', 'barbero', 'metodo_pago', 'total', 'fecha']
    list_filter = ['metodo_pago', 'fecha', 'barbero']
    inlines = [ItemVentaInline]
    readonly_fields = ['fecha', 'subtotal', 'total']

@admin.register(CorteCaja)
class CorteCajaAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'efectivo', 'qr', 'tarjeta', 'total', 'cerrado_por']
    readonly_fields = ['creado_en']
