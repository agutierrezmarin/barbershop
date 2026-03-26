from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'rol', 'email', 'activo']
    list_filter = ['rol', 'activo', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Barbería', {'fields': ('rol', 'telefono', 'foto', 'activo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Barbería', {'fields': ('rol', 'telefono')}),
    )
