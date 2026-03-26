from django.urls import path
from . import views
app_name = 'barberos'
urlpatterns = [
    path('', views.lista_barberos, name='lista'),
    path('nuevo/', views.nuevo_barbero, name='nuevo'),
    path('<int:pk>/', views.detalle_barbero, name='detalle'),
    path('<int:pk>/editar/', views.editar_barbero, name='editar'),
    path('<int:pk>/horarios/', views.horarios_barbero, name='horarios'),
    path('asistencia/', views.registrar_asistencia, name='asistencia'),
]
