from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta


@login_required
def dashboard(request):
    from apps.citas.models import Cita
    from apps.ventas.models import Venta
    from apps.inventario.models import Producto
    from apps.clientes.models import Cliente

    hoy = timezone.now().date()
    usuario = request.user

    # Citas de hoy
    citas_hoy = Cita.objects.filter(
        fecha_hora__date=hoy,
        estado__in=['pendiente', 'confirmado']
    )
    if usuario.rol == 'barbero':
        try:
            citas_hoy = citas_hoy.filter(barbero=usuario.perfil_barbero)
        except Exception:
            citas_hoy = Cita.objects.none()

    # Ingresos del día
    ventas_hoy = Venta.objects.filter(fecha__date=hoy)
    ingresos_hoy = sum(v.total for v in ventas_hoy)

    # Alertas de stock
    productos_bajo_stock = Producto.objects.filter(activo=True, stock_actual__lte=5)

    # Clientes nuevos este mes
    inicio_mes = hoy.replace(day=1)
    clientes_mes = Cliente.objects.filter(fecha_registro__date__gte=inicio_mes).count()

    context = {
        'citas_hoy': citas_hoy,
        'ingresos_hoy': ingresos_hoy,
        'productos_bajo_stock': productos_bajo_stock,
        'clientes_mes': clientes_mes,
        'total_citas_hoy': citas_hoy.count(),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def perfil(request):
    from .forms import PerfilForm, FotoPerfilForm, CambiarPasswordForm
    from django.contrib import messages
    from django.contrib.auth import update_session_auth_hash

    usuario = request.user
    perfil_form   = PerfilForm(instance=usuario)
    foto_form     = FotoPerfilForm(instance=usuario)
    password_form = CambiarPasswordForm(user=usuario)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'perfil':
            perfil_form = PerfilForm(request.POST, instance=usuario)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, 'Perfil actualizado correctamente.')
                return redirect('accounts:perfil')
            else:
                messages.error(request, 'Corrige los errores en el formulario.')

        elif accion == 'foto':
            foto_form = FotoPerfilForm(request.POST, request.FILES, instance=usuario)
            if foto_form.is_valid():
                # Eliminar foto anterior si existe
                if usuario.foto and 'foto' in request.FILES:
                    import os
                    if os.path.isfile(usuario.foto.path):
                        os.remove(usuario.foto.path)
                foto_form.save()
                messages.success(request, 'Foto de perfil actualizada.')
                return redirect('accounts:perfil')

        elif accion == 'quitar_foto':
            if usuario.foto:
                import os
                if os.path.isfile(usuario.foto.path):
                    os.remove(usuario.foto.path)
                usuario.foto = None
                usuario.save()
                messages.success(request, 'Foto de perfil eliminada.')
            return redirect('accounts:perfil')

        elif accion == 'password':
            password_form = CambiarPasswordForm(user=usuario, data=request.POST)
            if password_form.is_valid():
                usuario.set_password(password_form.cleaned_data['password_nueva'])
                usuario.save()
                update_session_auth_hash(request, usuario)
                messages.success(request, 'Contraseña cambiada correctamente.')
                return redirect('accounts:perfil')
            else:
                messages.error(request, 'Revisa los campos de contraseña.')

    return render(request, 'accounts/perfil.html', {
        'usuario':       usuario,
        'perfil_form':   perfil_form,
        'foto_form':     foto_form,
        'password_form': password_form,
    })
