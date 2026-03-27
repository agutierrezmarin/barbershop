from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.utils import no_barbero
from .models import Cliente
from .forms import ClienteForm

@login_required
def lista_clientes(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.filter(activo=True)
    if q:
        clientes = clientes.filter(nombre__icontains=q) | clientes.filter(telefono__icontains=q)
    return render(request, 'clientes/lista.html', {'clientes': clientes, 'q': q})

@login_required
@no_barbero
def nuevo_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente {cliente.nombre} registrado.')
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Nuevo Cliente'})

@login_required
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    citas = cliente.citas.select_related('barbero__usuario', 'servicio').order_by('-fecha_hora')[:20]
    return render(request, 'clientes/detalle.html', {'cliente': cliente, 'citas': citas})

@login_required
@no_barbero
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado.')
            return redirect('clientes:detalle', pk=pk)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Editar Cliente', 'cliente': cliente})
