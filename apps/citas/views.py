import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from datetime import timedelta, datetime, time
from .models import Cita
from .forms import CitaForm
from apps.barberos.models import Barbero, HorarioLaboral

# Paleta de colores por barbero (índice)
BARBERO_COLORS = [
    '#c8a951', '#5a7aa8', '#5a8a5a', '#a06050',
    '#7a5aaa', '#4a8a9a', '#aa7a4a', '#6a8a4a',
]


def _color_barbero(barbero_pk, barberos_ordenados):
    try:
        idx = list(barberos_ordenados).index(barbero_pk)
    except ValueError:
        idx = 0
    return BARBERO_COLORS[idx % len(BARBERO_COLORS)]


# ─── Vistas principales ────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    from apps.clientes.models import Cliente
    from apps.ventas.models import Venta
    from apps.inventario.models import Producto
    from django.db.models import Sum, Count
    from decimal import Decimal

    ahora = timezone.now()
    hoy   = ahora.date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes    = hoy.replace(day=1)

    citas_hoy = Cita.objects.filter(fecha_hora__date=hoy).select_related(
        'cliente', 'barbero__usuario', 'servicio'
    ).order_by('fecha_hora')

    ventas_hoy_qs = Venta.objects.filter(fecha__date=hoy)

    barbero_actual = None
    if request.user.es_barbero:
        try:
            barbero_actual = request.user.perfil_barbero
            citas_hoy      = citas_hoy.filter(barbero=barbero_actual)
            ventas_hoy_qs  = ventas_hoy_qs.filter(barbero=barbero_actual)
        except Exception:
            citas_hoy     = citas_hoy.none()
            ventas_hoy_qs = ventas_hoy_qs.none()

    # ── Conteos citas hoy ─────────────────────────────────────────────────────
    total_citas      = citas_hoy.count()
    citas_pendientes = citas_hoy.filter(estado__in=['pendiente', 'confirmado']).count()
    citas_atendidas  = citas_hoy.filter(estado='atendido').count()

    # ── Ingresos hoy ──────────────────────────────────────────────────────────
    ingresos_hoy  = ventas_hoy_qs.aggregate(t=Sum('total'))['t'] or Decimal('0')
    ventas_count  = ventas_hoy_qs.count()

    # ── Datos del mes (comunes a todos los roles) ──────────────────────────────
    citas_mes_qs    = Cita.objects.filter(fecha_hora__date__gte=inicio_mes)
    ventas_mes_qs   = Venta.objects.filter(fecha__date__gte=inicio_mes)
    if request.user.es_barbero and barbero_actual:
        citas_mes_qs  = citas_mes_qs.filter(barbero=barbero_actual)
        ventas_mes_qs = ventas_mes_qs.filter(barbero=barbero_actual)

    citas_mes    = citas_mes_qs.count()
    ingresos_mes = ventas_mes_qs.aggregate(t=Sum('total'))['t'] or Decimal('0')

    context = {
        'citas_hoy':        citas_hoy,
        'total_citas':      total_citas,
        'citas_pendientes': citas_pendientes,
        'citas_atendidas':  citas_atendidas,
        'ingresos_hoy':     ingresos_hoy,
        'ventas_count':     ventas_count,
        'citas_mes':        citas_mes,
        'ingresos_mes':     ingresos_mes,
        'hoy':              hoy,
    }

    # ── Datos extras solo para admin/recepcionista ────────────────────────────
    if not request.user.es_barbero:
        productos_bajo_stock = Producto.objects.filter(
            activo=True, stock_actual__lte=5
        ).count()

        # Rendimiento por barbero hoy
        barberos_hoy = []
        for b in Barbero.objects.filter(activo=True).select_related('usuario'):
            citas_b   = citas_hoy.filter(barbero=b)
            ventas_b  = Venta.objects.filter(fecha__date=hoy, barbero=b)
            ing_b     = ventas_b.aggregate(t=Sum('total'))['t'] or Decimal('0')
            comision_b = (ing_b * (b.comision_porcentaje or Decimal('0')) / 100).quantize(Decimal('0.01'))
            barberos_hoy.append({
                'barbero':    b,
                'total':      citas_b.count(),
                'atendidas':  citas_b.filter(estado='atendido').count(),
                'pendientes': citas_b.filter(estado__in=['pendiente', 'confirmado']).count(),
                'ingresos':   ing_b,
                'comision':   comision_b,
                'neto':       ing_b - comision_b,
            })
        barberos_hoy.sort(key=lambda x: x['ingresos'], reverse=True)

        ventas_recientes = (Venta.objects
                            .filter(fecha__date=hoy)
                            .select_related('barbero__usuario', 'cliente')
                            .order_by('-fecha')[:6])

        context.update({
            'productos_bajo_stock': productos_bajo_stock,
            'barberos_hoy':         barberos_hoy,
            'ventas_recientes':     ventas_recientes,
        })

    return render(request, 'citas/dashboard.html', context)


@login_required
def lista_citas(request):
    citas = Cita.objects.select_related('cliente', 'barbero__usuario', 'servicio').all()
    if request.user.es_barbero:
        try:
            citas = citas.filter(barbero=request.user.perfil_barbero)
        except Exception:
            citas = citas.none()
    fecha = request.GET.get('fecha')
    barbero_id = request.GET.get('barbero')
    estado = request.GET.get('estado')
    if fecha:
        citas = citas.filter(fecha_hora__date=fecha)
    if barbero_id and not request.user.es_barbero:
        citas = citas.filter(barbero_id=barbero_id)
    if estado:
        citas = citas.filter(estado=estado)
    barberos = Barbero.objects.filter(activo=True).select_related('usuario')
    return render(request, 'citas/lista.html', {
        'citas': citas[:100],
        'barberos': barberos,
        'estados': Cita.Estado.choices,
    })


@login_required
def nueva_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            try:
                cita = form.save()
                messages.success(request, f'Cita agendada para {cita.cliente} con {cita.barbero}')
                return redirect('citas:lista')
            except Exception as e:
                messages.error(request, f'Error: {e}')
    else:
        form = CitaForm()
    return render(request, 'citas/form.html', {'form': form, 'titulo': 'Nueva Cita'})


@login_required
def detalle_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.user.es_barbero:
        try:
            if cita.barbero != request.user.perfil_barbero:
                messages.error(request, 'Solo puedes ver tus propias citas.')
                return redirect('citas:lista')
        except Exception:
            return redirect('citas:dashboard')
    return render(request, 'citas/detalle.html', {'cita': cita})


@login_required
def editar_cita(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.user.es_barbero:
        try:
            if cita.barbero != request.user.perfil_barbero:
                messages.error(request, 'Solo puedes editar tus propias citas.')
                return redirect('citas:lista')
        except Exception:
            return redirect('citas:dashboard')
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Cita actualizada.')
                return redirect('citas:lista')
            except Exception as e:
                messages.error(request, f'Error: {e}')
    else:
        form = CitaForm(instance=cita)
    return render(request, 'citas/form.html', {'form': form, 'titulo': 'Editar Cita', 'cita': cita})


@login_required
def cambiar_estado(request, pk):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Cita.Estado.choices):
            cita.estado = nuevo_estado
            cita.save()
            messages.success(request, f'Estado cambiado a {cita.get_estado_display()}')
    return redirect('citas:lista')


@login_required
def agenda_barbero(request):
    """Vista principal del calendario interactivo."""
    barberos = Barbero.objects.filter(activo=True).select_related('usuario')
    colores = {}
    pks = list(barberos.values_list('pk', flat=True))
    for i, pk in enumerate(pks):
        colores[pk] = BARBERO_COLORS[i % len(BARBERO_COLORS)]
    return render(request, 'citas/agenda.html', {
        'barberos': barberos,
        'colores_barberos': colores,
    })


@login_required
def api_verificar_conflicto(request):
    """API: verifica si el barbero tiene cita que se superpone con el horario dado."""
    from datetime import timedelta
    barbero_id = request.GET.get('barbero')
    fecha_str  = request.GET.get('fecha_hora')
    duracion   = int(request.GET.get('duracion', 30))
    excluir_pk = request.GET.get('excluir')

    if not barbero_id or not fecha_str:
        return JsonResponse({'conflicto': False})

    try:
        barbero    = Barbero.objects.get(pk=barbero_id)
        fecha_hora = parse_datetime(fecha_str)
        if not fecha_hora:
            return JsonResponse({'conflicto': False})
        if timezone.is_naive(fecha_hora):
            fecha_hora = timezone.make_aware(fecha_hora)

        hora_fin = fecha_hora + timedelta(minutes=duracion)

        qs = Cita.objects.filter(
            barbero=barbero,
            estado__in=['pendiente', 'confirmado'],
            fecha_hora__lt=hora_fin,
        ).select_related('cliente', 'servicio')
        if excluir_pk:
            qs = qs.exclude(pk=excluir_pk)

        for cita in qs:
            if cita.hora_fin > fecha_hora:
                return JsonResponse({
                    'conflicto':    True,
                    'cliente':      cita.cliente.nombre,
                    'barbero':      str(barbero),
                    'hora_inicio':  cita.fecha_hora.strftime('%H:%M'),
                    'hora_fin':     cita.hora_fin.strftime('%H:%M'),
                    'fecha':        cita.fecha_hora.strftime('%d/%m/%Y'),
                    'servicio':     cita.servicio.nombre if cita.servicio else '—',
                    'cita_pk':      cita.pk,
                })
        return JsonResponse({'conflicto': False})
    except Exception:
        return JsonResponse({'conflicto': False})


@login_required
def slots_disponibles(request):
    barbero_id = request.GET.get('barbero')
    fecha_str = request.GET.get('fecha')
    servicio_minutos = int(request.GET.get('minutos', 30))
    if not barbero_id or not fecha_str:
        return JsonResponse({'slots': []})
    try:
        barbero = Barbero.objects.get(pk=barbero_id)
        fecha = datetime.fromisoformat(fecha_str).date()
        dia_semana = fecha.weekday()
        horario = HorarioLaboral.objects.filter(barbero=barbero, dia_semana=dia_semana, activo=True).first()
        if not horario:
            return JsonResponse({'slots': [], 'mensaje': 'Barbero no trabaja ese día'})
        slots = []
        actual = datetime.combine(fecha, horario.hora_inicio)
        fin_turno = datetime.combine(fecha, horario.hora_fin)
        citas_del_dia = Cita.objects.filter(
            barbero=barbero,
            fecha_hora__date=fecha,
            estado__in=['pendiente', 'confirmado']
        )
        while actual + timedelta(minutes=servicio_minutos) <= fin_turno:
            conflicto = any(
                actual < cita.hora_fin and actual + timedelta(minutes=servicio_minutos) > cita.fecha_hora
                for cita in citas_del_dia
            )
            if not conflicto:
                slots.append(actual.strftime('%H:%M'))
            actual += timedelta(minutes=30)
        return JsonResponse({'slots': slots})
    except Exception as e:
        return JsonResponse({'slots': [], 'error': str(e)})


# ─── API para FullCalendar ─────────────────────────────────────────────────────

@login_required
def api_recursos(request):
    """Barberos como recursos FullCalendar."""
    barberos = Barbero.objects.filter(activo=True).select_related('usuario').order_by('pk')
    recursos = []
    for i, b in enumerate(barberos):
        color = BARBERO_COLORS[i % len(BARBERO_COLORS)]
        recursos.append({
            'id': str(b.pk),
            'title': b.usuario.get_full_name() or b.usuario.username,
            'extendedProps': {'especialidad': b.especialidad or ''},
            'eventBackgroundColor': color,
            'eventBorderColor': color,
        })
    return JsonResponse(recursos, safe=False)


@login_required
def api_eventos(request):
    """Citas como eventos FullCalendar."""
    start = request.GET.get('start', '')
    end = request.GET.get('end', '')

    citas = Cita.objects.select_related('cliente', 'barbero__usuario', 'servicio').order_by('fecha_hora')
    if start:
        citas = citas.filter(fecha_hora__date__gte=start[:10])
    if end:
        citas = citas.filter(fecha_hora__date__lte=end[:10])
    if request.user.es_barbero:
        try:
            citas = citas.filter(barbero=request.user.perfil_barbero)
        except Exception:
            citas = citas.none()

    pks_barberos = list(Barbero.objects.filter(activo=True).order_by('pk').values_list('pk', flat=True))

    ESTADO_ALPHA = {'pendiente': 'dd', 'confirmado': 'ff', 'atendido': '88', 'cancelado': '55', 'no_show': '44'}

    eventos = []
    for cita in citas:
        try:
            idx = pks_barberos.index(cita.barbero_id)
        except ValueError:
            idx = 0
        color = BARBERO_COLORS[idx % len(BARBERO_COLORS)]
        eventos.append({
            'id': str(cita.pk),
            'resourceId': str(cita.barbero_id),
            'title': cita.cliente.nombre,
            'start': cita.fecha_hora.isoformat(),
            'end': cita.hora_fin.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'classNames': [f'estado-{cita.estado}'],
            'extendedProps': {
                'cliente_id': cita.cliente_id,
                'cliente_nombre': cita.cliente.nombre,
                'cliente_telefono': cita.cliente.telefono,
                'barbero_id': cita.barbero_id,
                'barbero_nombre': cita.barbero.usuario.get_full_name() or cita.barbero.usuario.username,
                'servicio_id': cita.servicio_id or '',
                'servicio_nombre': cita.servicio.nombre if cita.servicio else '—',
                'servicio_precio': str(cita.servicio.precio) if cita.servicio else '',
                'estado': cita.estado,
                'estado_display': cita.get_estado_display(),
                'duracion': cita.duracion_minutos,
                'notas': cita.notas,
                'precio_cobrado': str(cita.precio_cobrado) if cita.precio_cobrado else '',
            }
        })
    return JsonResponse(eventos, safe=False)


@login_required
def api_mover_cita(request, pk):
    """Actualiza fecha/hora y/o barbero de una cita (drag & drop)."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    cita = get_object_or_404(Cita, pk=pk)
    try:
        data = json.loads(request.body)
        if 'start' in data:
            dt = parse_datetime(data['start'])
            if dt:
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                cita.fecha_hora = dt
        if data.get('resourceId'):
            cita.barbero_id = int(data['resourceId'])
        cita.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_crear_cita(request):
    """Crea una cita desde el calendario."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    try:
        data = json.loads(request.body)
        dt = parse_datetime(data['start'])
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        cita = Cita(
            cliente_id=int(data['cliente_id']),
            barbero_id=int(data['barbero_id']),
            fecha_hora=dt,
            duracion_minutos=int(data.get('duracion', 30)),
            estado=data.get('estado', 'pendiente'),
            notas=data.get('notas', ''),
        )
        if data.get('servicio_id'):
            cita.servicio_id = int(data['servicio_id'])
        if data.get('precio'):
            cita.precio_cobrado = data['precio']
        cita.save()

        pks = list(Barbero.objects.filter(activo=True).order_by('pk').values_list('pk', flat=True))
        try:
            idx = pks.index(cita.barbero_id)
        except ValueError:
            idx = 0
        color = BARBERO_COLORS[idx % len(BARBERO_COLORS)]

        return JsonResponse({
            'ok': True,
            'evento': {
                'id': str(cita.pk),
                'resourceId': str(cita.barbero_id),
                'title': cita.cliente.nombre,
                'start': cita.fecha_hora.isoformat(),
                'end': cita.hora_fin.isoformat(),
                'backgroundColor': color,
                'borderColor': color,
                'classNames': [f'estado-{cita.estado}'],
                'extendedProps': {
                    'cliente_id': cita.cliente_id,
                    'cliente_nombre': cita.cliente.nombre,
                    'cliente_telefono': cita.cliente.telefono,
                    'barbero_id': cita.barbero_id,
                    'barbero_nombre': cita.barbero.usuario.get_full_name() or cita.barbero.usuario.username,
                    'servicio_id': cita.servicio_id or '',
                    'servicio_nombre': cita.servicio.nombre if cita.servicio else '—',
                    'estado': cita.estado,
                    'estado_display': cita.get_estado_display(),
                    'duracion': cita.duracion_minutos,
                    'notas': cita.notas,
                    'precio_cobrado': str(cita.precio_cobrado) if cita.precio_cobrado else '',
                }
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_actualizar_cita(request, pk):
    """Actualiza datos de una cita desde el modal de edición."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    cita = get_object_or_404(Cita, pk=pk)
    try:
        data = json.loads(request.body)
        if 'cliente_id' in data:
            cita.cliente_id = int(data['cliente_id'])
        if 'barbero_id' in data:
            cita.barbero_id = int(data['barbero_id'])
        if 'servicio_id' in data:
            cita.servicio_id = int(data['servicio_id']) if data['servicio_id'] else None
        if 'start' in data:
            dt = parse_datetime(data['start'])
            if dt:
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                cita.fecha_hora = dt
        if 'duracion' in data:
            cita.duracion_minutos = int(data['duracion'])
        if 'estado' in data:
            cita.estado = data['estado']
        if 'notas' in data:
            cita.notas = data['notas']
        if 'precio' in data:
            cita.precio_cobrado = data['precio'] or None
        cita.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_eliminar_cita(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    cita = get_object_or_404(Cita, pk=pk)
    cita.delete()
    return JsonResponse({'ok': True})


@login_required
def api_alertas_proximas(request):
    """Citas en los próximos 15 min o que acaban de comenzar (≤ 2 min pasados)."""
    from datetime import timedelta
    ahora = timezone.now()
    desde = ahora - timedelta(minutes=2)
    hasta = ahora + timedelta(minutes=15)

    citas = (Cita.objects
             .filter(fecha_hora__gte=desde, fecha_hora__lte=hasta,
                     estado__in=['pendiente', 'confirmado'])
             .select_related('cliente', 'barbero__usuario', 'servicio'))

    if request.user.es_barbero:
        try:
            citas = citas.filter(barbero=request.user.perfil_barbero)
        except Exception:
            citas = citas.none()

    alertas = []
    for c in citas:
        diff_seg = (c.fecha_hora - ahora).total_seconds()
        mins = int(diff_seg / 60)
        alertas.append({
            'id': c.pk,
            'cliente': c.cliente.nombre,
            'telefono': c.cliente.telefono,
            'barbero': c.barbero.usuario.get_full_name() or c.barbero.usuario.username,
            'servicio': c.servicio.nombre if c.servicio else '—',
            'hora': c.fecha_hora.strftime('%H:%M'),
            'mins_restantes': mins,
            'estado': c.estado,
        })
    return JsonResponse({'alertas': alertas})


@login_required
def api_buscar_clientes(request):
    q = request.GET.get('q', '').strip()
    from apps.clientes.models import Cliente
    clientes = Cliente.objects.filter(activo=True)
    if q:
        clientes = clientes.filter(Q(nombre__icontains=q) | Q(telefono__icontains=q))
    data = [{'id': c.pk, 'nombre': c.nombre, 'telefono': c.telefono} for c in clientes[:25]]
    return JsonResponse(data, safe=False)


@login_required
def api_servicios(request):
    from apps.servicios.models import Servicio
    servicios = Servicio.objects.filter(activo=True).select_related('categoria').order_by('nombre')
    data = [{
        'id': s.pk,
        'nombre': s.nombre,
        'duracion': s.duracion_minutos,
        'precio': str(s.precio),
    } for s in servicios]
    return JsonResponse(data, safe=False)
