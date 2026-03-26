from django.urls import path
from . import views
app_name = 'inventario'
urlpatterns = [
    path('', views.lista_productos, name='lista'),
    path('nuevo/', views.nuevo_producto, name='nuevo'),
    path('<int:pk>/editar/', views.editar_producto, name='editar'),
    path('<int:pk>/ajuste-stock/', views.ajuste_stock, name='ajuste_stock'),
    path('alertas/', views.alertas_stock, name='alertas'),
]
