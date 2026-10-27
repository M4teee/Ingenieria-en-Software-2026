from django.urls import path

from . import views

app_name = 'operario'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('comercios/', views.comercios, name='comercios'),
    path('comercios/nuevo/', views.nuevo_comercio, name='nuevo_comercio'),
    path('repartidores/', views.repartidores, name='repartidores'),
    path('repartidores/nuevo/', views.nuevo_repartidor, name='nuevo_repartidor'),
    path('pedidos/estado/', views.estado_pedidos, name='estado_pedidos'),
    path('pedidos/nuevo/', views.cargar_pedido, name='cargar_pedido'),
    path('pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path(
        'pedidos/<int:pedido_id>/asignar/',
        views.asignar_repartidor,
        name='asignar_repartidor',
    ),
    path(
        'pedidos/<int:pedido_id>/registrado/',
        views.pedido_registrado,
        name='pedido_registrado',
    ),
]
