from django.contrib import admin
from .models import Cita

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'barbero', 'servicio', 'fecha_hora', 'estado', 'duracion_minutos']
    list_filter = ['estado', 'barbero', 'fecha_hora']
    search_fields = ['cliente__nombre', 'barbero__usuario__username']
    date_hierarchy = 'fecha_hora'
