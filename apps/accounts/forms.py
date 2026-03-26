from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Usuario


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+591 7xx xxxxx'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name':  'Apellido',
            'email':      'Correo electrónico',
            'telefono':   'Teléfono',
        }


class FotoPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['foto']
        widgets = {
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class CambiarPasswordForm(forms.Form):
    password_actual = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
    )
    password_nueva = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        min_length=6,
    )
    password_confirmar = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password_actual(self):
        pwd = self.cleaned_data.get('password_actual')
        if not self.user.check_password(pwd):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return pwd

    def clean(self):
        cleaned = super().clean()
        nueva = cleaned.get('password_nueva')
        confirmar = cleaned.get('password_confirmar')
        if nueva and confirmar and nueva != confirmar:
            self.add_error('password_confirmar', 'Las contraseñas no coinciden.')
        if nueva:
            try:
                validate_password(nueva, self.user)
            except forms.ValidationError as e:
                self.add_error('password_nueva', e)
        return cleaned
