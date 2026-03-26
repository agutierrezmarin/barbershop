from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.utils import no_barbero
from .models import Barbero, HorarioLaboral, Asistencia
from .forms import UsuarioCrearForm, UsuarioEditarForm, BarberoPerfilForm, HorarioForm, AsistenciaForm


@login_required
@no_barbero
def lista_barberos(request):
    barberos = Barbero.objects.select_related('usuario').order_by('usuario__first_name')
    return render(request, 'barberos/lista.html', {'barberos': barberos})


@login_required
@no_barbero
def nuevo_barbero(request):
    if request.method == 'POST':
        usuario_form = UsuarioCrearForm(request.POST)
        barbero_form = BarberoPerfilForm(request.POST)
        if usuario_form.is_valid() and barbero_form.is_valid():
            usuario = usuario_form.save()
            barbero = barbero_form.save(commit=False)
            barbero.usuario = usuario
            barbero.save()
            barbero_form.save_m2m()
            messages.success(request, f'Barbero {usuario.get_full_name() or usuario.username} registrado correctamente.')
            return redirect('barberos:lista')
    else:
        usuario_form = UsuarioCrearForm()
        barbero_form = BarberoPerfilForm()
    return render(request, 'barberos/form.html', {
        'usuario_form': usuario_form,
        'barbero_form': barbero_form,
        'titulo': 'Nuevo Barbero',
    })


@login_required
@no_barbero
def detalle_barbero(request, pk):
    barbero = get_object_or_404(Barbero, pk=pk)
    return render(request, 'barberos/detalle.html', {'barbero': barbero})


@login_required
@no_barbero
def editar_barbero(request, pk):
    barbero = get_object_or_404(Barbero, pk=pk)
    if request.method == 'POST':
        usuario_form = UsuarioEditarForm(request.POST, instance=barbero.usuario)
        barbero_form = BarberoPerfilForm(request.POST, instance=barbero)
        if usuario_form.is_valid() and barbero_form.is_valid():
            usuario_form.save()
            barbero_form.save()
            messages.success(request, 'Barbero actualizado correctamente.')
            return redirect('barberos:lista')
    else:
        usuario_form = UsuarioEditarForm(instance=barbero.usuario)
        barbero_form = BarberoPerfilForm(instance=barbero)
    return render(request, 'barberos/form.html', {
        'usuario_form': usuario_form,
        'barbero_form': barbero_form,
        'titulo': 'Editar Barbero',
        'barbero': barbero,
    })


@login_required
@no_barbero
def horarios_barbero(request, pk):
    barbero = get_object_or_404(Barbero, pk=pk)
    horarios = barbero.horarios.all().order_by('dia_semana')
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.barbero = barbero
            horario.save()
            messages.success(request, 'Horario guardado.')
            return redirect('barberos:horarios', pk=pk)
    else:
        form = HorarioForm()
    return render(request, 'barberos/horarios.html', {'barbero': barbero, 'horarios': horarios, 'form': form})


@login_required
@no_barbero
def registrar_asistencia(request):
    if request.method == 'POST':
        form = AsistenciaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asistencia registrada.')
            return redirect('barberos:lista')
    else:
        form = AsistenciaForm()
    return render(request, 'barberos/asistencia.html', {'form': form})
