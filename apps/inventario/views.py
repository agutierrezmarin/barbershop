from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.utils import no_barbero
from .models import Producto, MovimientoStock
from .forms import ProductoForm, AjusteStockForm

@login_required
def lista_productos(request):
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    return render(request, 'inventario/lista.html', {'productos': productos})

@login_required
def nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto registrado.')
            return redirect('inventario:lista')
    else:
        form = ProductoForm()
    return render(request, 'inventario/form.html', {'form': form, 'titulo': 'Nuevo Producto'})

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('inventario:lista')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/form.html', {'form': form, 'titulo': 'Editar Producto', 'producto': producto})

@login_required
def ajuste_stock(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = AjusteStockForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data['tipo']
            cantidad = form.cleaned_data['cantidad']
            notas = form.cleaned_data['notas']
            stock_anterior = producto.stock_actual
            if tipo == 'entrada':
                producto.stock_actual += cantidad
            elif tipo == 'salida':
                producto.stock_actual -= cantidad
            else:
                producto.stock_actual = cantidad
            producto.save()
            MovimientoStock.objects.create(
                producto=producto, tipo=tipo, cantidad=cantidad,
                stock_anterior=stock_anterior, stock_nuevo=producto.stock_actual, notas=notas
            )
            messages.success(request, f'Stock ajustado. Nuevo stock: {producto.stock_actual}')
            return redirect('inventario:lista')
    else:
        form = AjusteStockForm()
    return render(request, 'inventario/ajuste_stock.html', {'form': form, 'producto': producto})

@login_required
def alertas_stock(request):
    productos = Producto.objects.filter(activo=True, stock_actual__lte=5)
    return render(request, 'inventario/alertas.html', {'productos': productos})
