from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        BARBERO = 'barbero', 'Barbero'
        RECEPCIONISTA = 'recepcionista', 'Recepcionista'

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.RECEPCIONISTA)
    telefono = models.CharField(max_length=20, blank=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    @property
    def es_barbero(self):
        return self.rol == self.Rol.BARBERO
