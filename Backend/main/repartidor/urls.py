from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='repartidor'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='repartidor_detalle_pedido'),
    path('historial/', views.historial_entregas, name='historial_entregas'),
    path('evidencia/<int:historial_id>/', views.ver_fotografia, name='repartidor_fotografia'),
    path(
        'pedido/<int:pedido_id>/actualizar-estado/',
        views.actualizar_estado,
        name='actualizar_estado'
    ),
    path('pedido/<int:pedido_id>/aceptar/', views.aceptar, name='repartidor_aceptar'),
    path('pedido/<int:pedido_id>/rechazar/', views.rechazar, name='repartidor_rechazar'),
    path('login-pin/', views.login_pin, name='repartidor_login_pin'),
    path(
        'disponibilidad/',
        views.toggle_disponibilidad,
        name='repartidor_toggle_disponibilidad',
    ),
]
