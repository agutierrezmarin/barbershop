from django import forms
from django.contrib.auth import get_user_model
from .models import Barbero, HorarioLaboral, Asistencia

Usuario = get_user_model()


class UsuarioCrearForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=6,
    )
    confirmar_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono':   forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirmar_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirmar_password', 'Las contraseñas no coinciden.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.rol = 'barbero'
        if commit:
            user.save()
        return user


class UsuarioEditarForm(forms.ModelForm):
    nueva_password = forms.CharField(
        label='Nueva contraseña (dejar vacío para no cambiar)',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        min_length=6,
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono':   forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        nueva = self.cleaned_data.get('nueva_password')
        if nueva:
            user.set_password(nueva)
        if commit:
            user.save()
        return user


class BarberoPerfilForm(forms.ModelForm):
    class Meta:
        model = Barbero
        fields = ['especialidad', 'bio', 'comision_porcentaje', 'servicios', 'activo']
        widgets = {
            'especialidad':        forms.TextInput(attrs={'class': 'form-control'}),
            'bio':                 forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comision_porcentaje': forms.NumberInput(attrs={'class': 'form-control'}),
            'servicios':           forms.CheckboxSelectMultiple(),
        }


# Alias para no romper imports existentes
BarberoForm = BarberoPerfilForm


class HorarioForm(forms.ModelForm):
    class Meta:
        model = HorarioLaboral
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'activo']
        widgets = {
            'dia_semana':  forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin':    forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }


class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['barbero', 'fecha', 'hora_entrada', 'hora_salida', 'notas']
        widgets = {
            'barbero':      forms.Select(attrs={'class': 'form-select'}),
            'fecha':        forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_entrada': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_salida':  forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notas':        forms.TextInput(attrs={'class': 'form-control'}),
        }
