from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class Cita(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        CONFIRMADO = 'confirmado', 'Confirmado'
        ATENDIDO = 'atendido', 'Atendido'
        CANCELADO = 'cancelado', 'Cancelado'
        NO_SHOW = 'no_show', 'No Show'

    class BloquesTiempo(models.IntegerChoices):
        QUINCE        = 15,  '15 minutos'
        TREINTA       = 30,  '30 minutos'
        CUARENTA_CINCO = 45, '45 minutos'
        SESENTA       = 60,  '60 minutos'
        NOVENTA       = 90,  '90 minutos'
        CIENTO_VEINTE = 120, '120 minutos'

    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='citas')
    barbero = models.ForeignKey('barberos.Barbero', on_delete=models.CASCADE, related_name='citas')
    servicio = models.ForeignKey('servicios.Servicio', on_delete=models.SET_NULL, null=True, related_name='citas')
    fecha_hora = models.DateTimeField()
    duracion_minutos = models.IntegerField(choices=BloquesTiempo.choices, default=BloquesTiempo.TREINTA)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    notas = models.TextField(blank=True)
    precio_cobrado = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.cliente} con {self.barbero} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"

    @property
    def hora_fin(self):
        return self.fecha_hora + timedelta(minutes=self.duracion_minutos)

    def clean(self):
        # Detectar conflictos de horario para el mismo barbero
        if self.fecha_hora and self.barbero_id:
            conflictos = Cita.objects.filter(
                barbero=self.barbero,
                estado__in=['pendiente', 'confirmado'],
                fecha_hora__lt=self.fecha_hora + timedelta(minutes=self.duracion_minutos),
            ).exclude(pk=self.pk)

            for cita in conflictos:
                if cita.hora_fin > self.fecha_hora:
                    raise ValidationError(
                        f'Conflicto de horario: {self.barbero} ya tiene una cita de '
                        f'{cita.fecha_hora.strftime("%H:%M")} a {cita.hora_fin.strftime("%H:%M")}'
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
