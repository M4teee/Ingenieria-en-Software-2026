from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='repartidor'),
    path('pedido/<int:pedido_id>/aceptar/', views.aceptar, name='repartidor_aceptar'),
    path('pedido/<int:pedido_id>/rechazar/', views.rechazar, name='repartidor_rechazar'),
]
