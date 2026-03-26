from django.contrib import admin
from .models import Notificacion

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['destinatario', 'canal', 'estado', 'creado_en']
    list_filter = ['canal', 'estado']
