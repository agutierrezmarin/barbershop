from django.urls import path
from . import views
app_name = 'servicios'
urlpatterns = [
    path('', views.lista_servicios, name='lista'),
    path('nuevo/', views.nuevo_servicio, name='nuevo'),
    path('<int:pk>/editar/', views.editar_servicio, name='editar'),
]
