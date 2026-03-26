from django.urls import path
from . import views
app_name = 'ventas'
urlpatterns = [
    path('', views.lista_ventas, name='lista'),
    path('nueva/', views.nueva_venta, name='nueva'),
    path('<int:pk>/', views.detalle_venta, name='detalle'),
    path('corte-caja/', views.corte_caja, name='corte_caja'),
    path('corte-caja/realizar/', views.realizar_corte, name='realizar_corte'),
    path('reporte/excel/', views.exportar_excel, name='exportar_excel'),
]
