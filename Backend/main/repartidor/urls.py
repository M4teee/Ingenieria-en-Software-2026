from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='repartidor'),
    path(
        'pedido/<int:pedido_id>/actualizar-estado/',
        views.actualizar_estado,
        name='actualizar_estado'
    ),
]