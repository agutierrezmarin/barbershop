from django.urls import path
from . import views
app_name = 'reportes'
urlpatterns = [
    path('', views.reporte_general, name='general'),
    path('ingresos/', views.reporte_ingresos, name='ingresos'),
    path('servicios/', views.reporte_servicios, name='servicios'),
    path('barberos/', views.reporte_barberos, name='barberos'),
    path('barberos/excel/', views.exportar_barberos_excel, name='barberos_excel'),
    path('clientes/', views.reporte_clientes, name='clientes'),
    path('historial/', views.reporte_historial, name='historial'),
    path('historial/excel/', views.exportar_historial_excel, name='historial_excel'),
]
