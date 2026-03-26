from django.contrib import admin
from .models import CategoriaServicio, Servicio

@admin.register(CategoriaServicio)
class CategoriaServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre']

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'duracion_minutos', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre']
