from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    preferencias = models.TextField(blank=True, help_text='Ej: siempre degradado, barba corta')
    notas_internas = models.TextField(blank=True, help_text='Solo visible para el staff')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.telefono})"

    @property
    def total_visitas(self):
        return self.citas.filter(estado='atendido').count()

    @property
    def ultima_visita(self):
        ultima = self.citas.filter(estado='atendido').order_by('-fecha_hora').first()
        return ultima.fecha_hora if ultima else None
