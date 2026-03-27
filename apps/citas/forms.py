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

    def clean(self):
        from datetime import timedelta
        from django.utils import timezone as tz
        cleaned_data = super().clean()
        barbero = cleaned_data.get('barbero')
        fecha_hora = cleaned_data.get('fecha_hora')
        duracion = int(cleaned_data.get('duracion_minutos') or 30)

        if barbero and fecha_hora:
            if tz.is_naive(fecha_hora):
                fecha_hora = tz.make_aware(fecha_hora)
            hora_fin = fecha_hora + timedelta(minutes=duracion)

            qs = Cita.objects.filter(
                barbero=barbero,
                estado__in=['pendiente', 'confirmado'],
                fecha_hora__lt=hora_fin,
            ).select_related('cliente')
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            for cita in qs:
                if cita.hora_fin > fecha_hora:
                    raise forms.ValidationError(
                        f'Conflicto: {barbero} ya tiene una cita con '
                        f'{cita.cliente.nombre} de '
                        f'{cita.fecha_hora.strftime("%H:%M")} a {cita.hora_fin.strftime("%H:%M")}. '
                        f'Elige otro horario.'
                    )
        return cleaned_data
