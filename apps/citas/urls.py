from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    # Vistas principales
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('citas/', views.lista_citas, name='lista'),
    path('citas/nueva/', views.nueva_cita, name='nueva'),
    path('citas/<int:pk>/', views.detalle_cita, name='detalle'),
    path('citas/<int:pk>/editar/', views.editar_cita, name='editar'),
    path('citas/<int:pk>/estado/', views.cambiar_estado, name='cambiar_estado'),
    path('citas/agenda/', views.agenda_barbero, name='agenda'),
    path('api/slots-disponibles/', views.slots_disponibles, name='slots_disponibles'),
    path('api/verificar-conflicto/', views.api_verificar_conflicto, name='api_verificar_conflicto'),

    # API para FullCalendar
    path('api/agenda/recursos/', views.api_recursos, name='api_recursos'),
    path('api/agenda/eventos/', views.api_eventos, name='api_eventos'),
    path('api/agenda/citas/crear/', views.api_crear_cita, name='api_crear_cita'),
    path('api/agenda/citas/<int:pk>/mover/', views.api_mover_cita, name='api_mover_cita'),
    path('api/agenda/citas/<int:pk>/actualizar/', views.api_actualizar_cita, name='api_actualizar_cita'),
    path('api/agenda/citas/<int:pk>/eliminar/', views.api_eliminar_cita, name='api_eliminar_cita'),
    path('api/agenda/clientes/', views.api_buscar_clientes, name='api_buscar_clientes'),
    path('api/alertas-proximas/', views.api_alertas_proximas, name='api_alertas_proximas'),
    path('api/agenda/servicios/', views.api_servicios, name='api_servicios'),
]
