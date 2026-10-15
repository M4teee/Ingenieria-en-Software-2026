from django.urls import path

from . import views

app_name = 'operario'

urlpatterns = [
    path('', views.cargar_pedido, name='inicio'),
    path('pedidos/nuevo/', views.cargar_pedido, name='cargar_pedido'),
    path(
        'pedidos/<int:pedido_id>/registrado/',
        views.pedido_registrado,
        name='pedido_registrado',
    ),
]
