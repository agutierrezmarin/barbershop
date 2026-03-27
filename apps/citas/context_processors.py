from django.utils import timezone


def notificaciones_navbar(request):
    if not request.user.is_authenticated:
        return {}

    try:
        from .models import Cita
        ahora = timezone.now()
        hoy   = ahora.date()

        qs_base = Cita.objects.all()
        if request.user.es_barbero:
            try:
                qs_base = qs_base.filter(barbero=request.user.perfil_barbero)
            except Exception:
                qs_base = Cita.objects.none()

        # Citas de HOY (todos los estados) para contar totales
        qs_hoy_all = qs_base.filter(fecha_hora__date=hoy)

        # Citas activas de hoy (pendiente o confirmado)
        citas_hoy_qs = (qs_hoy_all
                        .filter(estado__in=['pendiente', 'confirmado'])
                        .select_related('cliente', 'barbero__usuario', 'servicio')
                        .order_by('fecha_hora'))

        # Próxima cita aún no llegada
        proxima = citas_hoy_qs.filter(fecha_hora__gte=ahora).first()

        # Slice para el modal
        citas_hoy = citas_hoy_qs[:10]

        # Pasadas HOY sin atender (no días anteriores)
        sin_atender = (qs_hoy_all
                       .filter(fecha_hora__lt=ahora, estado__in=['pendiente', 'confirmado'])
                       .count())

        # Totales del día para el resumen del admin
        total_hoy      = qs_hoy_all.count()
        atendidas_hoy  = qs_hoy_all.filter(estado='atendido').count()
        pendientes_hoy = citas_hoy_qs.count()

        # Ingresos de hoy (solo admin/recepcionista)
        ingresos_hoy = None
        if not request.user.es_barbero:
            try:
                from apps.ventas.models import Venta
                from django.db.models import Sum
                ingresos_hoy = (Venta.objects.filter(fecha__date=hoy)
                                .aggregate(t=Sum('total'))['t'] or 0)
            except Exception:
                ingresos_hoy = 0

        total_notif = pendientes_hoy + sin_atender

        return {
            'nav_citas_hoy':      citas_hoy,
            'nav_sin_atender':    sin_atender,
            'nav_proxima':        proxima,
            'nav_notif_count':    total_notif,
            'nav_total_hoy':      total_hoy,
            'nav_atendidas_hoy':  atendidas_hoy,
            'nav_pendientes_hoy': pendientes_hoy,
            'nav_ingresos_hoy':   ingresos_hoy,
        }
    except Exception:
        return {}
