from django.utils import timezone


def notificaciones_navbar(request):
    if not request.user.is_authenticated:
        return {}

    try:
        from .models import Cita
        ahora = timezone.now()
        hoy   = ahora.date()

        # Filtrar por barbero si el usuario tiene ese rol
        qs_base = Cita.objects.all()
        if request.user.es_barbero:
            try:
                qs_base = qs_base.filter(barbero=request.user.perfil_barbero)
            except Exception:
                qs_base = Cita.objects.none()

        # Citas activas de hoy (pendiente o confirmado) — sin slice para poder filtrar
        citas_hoy_qs = (qs_base
                        .filter(fecha_hora__date=hoy, estado__in=['pendiente', 'confirmado'])
                        .select_related('cliente', 'barbero__usuario', 'servicio')
                        .order_by('fecha_hora'))

        # Próxima cita (antes del slice)
        proxima = citas_hoy_qs.filter(fecha_hora__gte=ahora).first()

        # Slice para el dropdown
        citas_hoy = citas_hoy_qs[:8]

        # Citas pasadas sin atender
        sin_atender = (qs_base
                       .filter(fecha_hora__lt=ahora, estado__in=['pendiente', 'confirmado'])
                       .count())

        total_notif = citas_hoy_qs.count() + sin_atender

        return {
            'nav_citas_hoy':   citas_hoy,
            'nav_sin_atender': sin_atender,
            'nav_proxima':     proxima,
            'nav_notif_count': total_notif,
        }
    except Exception:
        return {}
