from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('', include('apps.citas.urls', namespace='citas')),
    path('clientes/', include('apps.clientes.urls', namespace='clientes')),
    path('barberos/', include('apps.barberos.urls', namespace='barberos')),
    path('servicios/', include('apps.servicios.urls', namespace='servicios')),
    path('ventas/', include('apps.ventas.urls', namespace='ventas')),
    path('inventario/', include('apps.inventario.urls', namespace='inventario')),
    path('reportes/', include('apps.reportes.urls', namespace='reportes')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
