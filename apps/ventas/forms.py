from django import forms
from .models import Venta, ItemVenta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cita', 'barbero', 'cliente', 'metodo_pago', 'descuento', 'notas']
        widgets = {
            'cita': forms.Select(attrs={'class': 'form-select'}),
            'barbero': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
