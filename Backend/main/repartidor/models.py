from django.conf import settings
from django.db import models


class Pedido(models.Model):
    ESTADOS = [
        ('asignado', 'Asignado'),
        ('retirado', 'Retirado'),
        ('en_viaje', 'En viaje'),
        ('entregado', 'Entregado'),
        ('fallido', 'Fallido'),
    ]

    TRANSICIONES_PERMITIDAS = {
        'asignado': ['retirado'],
        'retirado': ['en_viaje'],
        'en_viaje': ['entregado', 'fallido'],
        'entregado': [],
        'fallido': [],
    }

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='asignado'
    )

    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos_asignados'
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']

    def puede_cambiar_a(self, nuevo_estado):
        return nuevo_estado in self.TRANSICIONES_PERMITIDAS.get(
            self.estado,
            []
        )

    def __str__(self):
        return self.codigo


class HistorialEstado(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='historial'
    )

    estado_anterior = models.CharField(
        max_length=20,
        blank=True
    )

    estado_nuevo = models.CharField(
        max_length=20,
        choices=Pedido.ESTADOS
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='cambios_estado_entrega'
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    fotografia = models.ImageField(
        upload_to='entregas/',
        blank=True,
        null=True
    )

    incidencia = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = 'Historial de estado'
        verbose_name_plural = 'Historial de estados'
        ordering = ['fecha']

    def __str__(self):
        return f'{self.pedido.codigo}: {self.estado_nuevo}'