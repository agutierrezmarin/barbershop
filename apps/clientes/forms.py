from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'email', 'fecha_nacimiento', 'preferencias', 'notas_internas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preferencias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notas_internas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Solo visible para el staff'}),
        }
