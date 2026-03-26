from django.db import models


class Notificacion(models.Model):
    class Canal(models.TextChoices):
        SMS = 'sms', 'SMS'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        INTERNO = 'interno', 'Interno'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        ENVIADO = 'enviado', 'Enviado'
        ERROR = 'error', 'Error'

    cita = models.ForeignKey('citas.Cita', on_delete=models.CASCADE, related_name='notificaciones', null=True, blank=True)
    canal = models.CharField(max_length=10, choices=Canal.choices, default=Canal.INTERNO)
    destinatario = models.CharField(max_length=100)
    mensaje = models.TextField()
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    enviado_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-creado_en']

    def __str__(self):
        return f"[{self.get_canal_display()}] {self.destinatario} - {self.estado}"
