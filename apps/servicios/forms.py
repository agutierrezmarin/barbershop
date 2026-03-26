from django import forms
from .models import Servicio, CategoriaServicio

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['categoria', 'nombre', 'descripcion', 'precio', 'duracion_minutos', 'activo', 'imagen']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
        }
