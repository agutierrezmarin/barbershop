from django.contrib import admin
from .models import Barbero, HorarioLaboral, Asistencia

class HorarioInline(admin.TabularInline):
    model = HorarioLaboral
    extra = 1

@admin.register(Barbero)
class BarberoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'especialidad', 'comision_porcentaje', 'activo']
    inlines = [HorarioInline]
    filter_horizontal = ['servicios']

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['barbero', 'fecha', 'hora_entrada', 'hora_salida']
    list_filter = ['barbero', 'fecha']
