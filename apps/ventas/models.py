from django.db import models
from django.conf import settings
from django.db import transaction


class Venta(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'efectivo', 'Efectivo'
        QR = 'qr', 'QR / Transferencia'
        TARJETA = 'tarjeta', 'Tarjeta'

    cita = models.OneToOneField('citas.Cita', on_delete=models.SET_NULL, null=True, blank=True, related_name='venta')
    barbero = models.ForeignKey('barberos.Barbero', on_delete=models.SET_NULL, null=True, related_name='ventas')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices, default=MetodoPago.EFECTIVO)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    atendido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha.strftime('%d/%m/%Y')} - Bs. {self.total}"

    def calcular_total(self):
        subtotal = sum(item.subtotal for item in self.items.all())
        self.subtotal = subtotal
        self.total = subtotal - self.descuento
        self.save()


class ItemVenta(models.Model):
    class TipoItem(models.TextChoices):
        SERVICIO = 'servicio', 'Servicio'
        PRODUCTO = 'producto', 'Producto'

    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    tipo = models.CharField(max_length=10, choices=TipoItem.choices)
    servicio = models.ForeignKey('servicios.Servicio', on_delete=models.SET_NULL, null=True, blank=True)
    producto = models.ForeignKey('inventario.Producto', on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Item de Venta'
        verbose_name_plural = 'Items de Venta'

    def __str__(self):
        return f"{self.descripcion} x{self.cantidad}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def save(self, *args, **kwargs):
        # Descontar stock si es producto
        if self.tipo == self.TipoItem.PRODUCTO and self.producto:
            if not self.pk:  # solo en creación
                with transaction.atomic():
                    prod = self.producto
                    prod.stock_actual -= self.cantidad
                    prod.save()
                    from apps.inventario.models import MovimientoStock
                    MovimientoStock.objects.create(
                        producto=prod,
                        tipo='salida',
                        cantidad=self.cantidad,
                        stock_anterior=prod.stock_actual + self.cantidad,
                        stock_nuevo=prod.stock_actual,
                        referencia=f'Venta #{self.venta.pk}'
                    )
        super().save(*args, **kwargs)


class CorteCaja(models.Model):
    fecha = models.DateField(unique=True)
    efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qr = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True)
    cerrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Corte de Caja'
        verbose_name_plural = 'Cortes de Caja'
        ordering = ['-fecha']

    def __str__(self):
        return f"Corte {self.fecha} - Bs. {self.total}"
