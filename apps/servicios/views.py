from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.utils import no_barbero
from .models import Servicio, CategoriaServicio
from .forms import ServicioForm

@login_required
@no_barbero
def lista_servicios(request):
    servicios = Servicio.objects.select_related('categoria').filter(activo=True)
    return render(request, 'servicios/lista.html', {'servicios': servicios})

@login_required
@no_barbero
def nuevo_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio registrado.')
            return redirect('servicios:lista')
    else:
        form = ServicioForm()
    return render(request, 'servicios/form.html', {'form': form, 'titulo': 'Nuevo Servicio'})

@login_required
@no_barbero
def editar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado.')
            return redirect('servicios:lista')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'servicios/form.html', {'form': form, 'titulo': 'Editar Servicio', 'servicio': servicio})
