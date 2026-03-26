from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def rol_requerido(*roles):
    """Permite acceso solo a los roles indicados. Redirige a dashboard si no autorizado."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.rol not in roles:
                messages.error(request, 'No tienes permiso para acceder a esta sección.')
                return redirect('citas:dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Shortcut: solo admin y recepcionista (no barberos)
def no_barbero(view_func):
    return rol_requerido('admin', 'recepcionista')(view_func)
