from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='repartidor'),
    path(
        'pedido/<int:pedido_id>/actualizar-estado/',
        views.actualizar_estado,
        name='actualizar_estado'
    ),
    path('login-pin/', views.login_pin, name='repartidor_login_pin'),
    path(
        'disponibilidad/',
        views.toggle_disponibilidad,
        name='repartidor_toggle_disponibilidad',
    ),
]
