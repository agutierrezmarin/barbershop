from django import forms
from .models import Cita
from apps.barberos.models import Barbero
from apps.clientes.models import Cliente
from apps.servicios.models import Servicio


class CitaForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label='Fecha y Hora'
    )

    class Meta:
        model = Cita
        fields = ['cliente', 'barbero', 'servicio', 'fecha_hora', 'duracion_minutos', 'estado', 'notas']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'barbero': forms.Select(attrs={'class': 'form-select'}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'duracion_minutos': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['barbero'].queryset = Barbero.objects.filter(activo=True).select_related('usuario')
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True).order_by('nombre')
        self.fields['servicio'].queryset = Servicio.objects.filter(activo=True).order_by('nombre')
        for field in self.fields.values():
            if not hasattr(field.widget, 'attrs'):
                field.widget.attrs = {}
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
