# main\repartidor\models.py

from django.conf import settings
from django.db import models

ESTADOS_PEDIDO = [
    ('registrado', 'Registrado'),
    ('asignado', 'Asignado'),
    ('retirado', 'Retirado'),
    ('en_viaje', 'En viaje'),
    ('entregado', 'Entregado'),
    ('fallido', 'Fallido'),
    ('cancelado', 'Cancelado'),
]

class RepartidorPerfil(models.Model):
    """Perfil de repartidor asociado a un User existente (no duplica User)."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_repartidor',
    )
    disponible = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Perfil de repartidor'
        verbose_name_plural = 'Perfiles de repartidor'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username}'

class Pedido(models.Model):
    comercio = models.ForeignKey(
        'operario.Comercio',
        on_delete=models.PROTECT,
        related_name='pedidos',
    )
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='registrado')
    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos',
    )
    fecha_hora_asignacion = models.DateTimeField(null=True, blank=True)
    # ponytail: expiración con pereza (cálculo al cargar); cron/tarea celery si hay many assignments
    LIMITE_ACEPTACION_SEGUNDOS = 300

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-id']

    def __str__(self):
        return f'Pedido #{self.id} ({self.get_estado_display()})'

class HistorialPedido(models.Model):
    """Auditoría de eventos de un pedido (asignaciones, aceptaciones, rechazos, etc.)."""
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='historial',
    )
    descripcion = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historial de pedido'
        verbose_name_plural = 'Historiales de pedidos'
        ordering = ['fecha_hora']

    def __str__(self):
        return f'{self.pedido} - {self.descripcion}'
