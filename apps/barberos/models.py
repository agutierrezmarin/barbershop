from django.db import models
from django.conf import settings
from apps.servicios.models import Servicio


class Barbero(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_barbero')
    servicios = models.ManyToManyField(Servicio, related_name='barberos', blank=True)
    comision_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=40.00, help_text='% de comisión por servicio')
    bio = models.TextField(blank=True)
    especialidad = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Barbero'
        verbose_name_plural = 'Barberos'

    def __str__(self):
        return str(self.usuario)


class HorarioLaboral(models.Model):
    DIAS = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'),
        (3, 'Jueves'), (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Horario Laboral'
        verbose_name_plural = 'Horarios Laborales'
        unique_together = ['barbero', 'dia_semana']
        ordering = ['dia_semana', 'hora_inicio']

    def __str__(self):
        return f"{self.barbero} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"


class Asistencia(models.Model):
    barbero = models.ForeignKey(Barbero, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    hora_entrada = models.TimeField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)
    notas = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ['barbero', 'fecha']
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.barbero} - {self.fecha}"
