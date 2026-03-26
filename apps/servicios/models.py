from django.db import models


class CategoriaServicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías de Servicio'

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    categoria = models.ForeignKey(CategoriaServicio, on_delete=models.SET_NULL, null=True, blank=True, related_name='servicios')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    duracion_minutos = models.PositiveIntegerField(default=30, help_text='Duración en minutos')
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - Bs. {self.precio}"
