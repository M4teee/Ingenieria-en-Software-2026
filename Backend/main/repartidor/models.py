import secrets
import string

from django.conf import settings
from django.db import models


class Repartidor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='repartidor',
    )
    pin = models.CharField(max_length=4, unique=True)
    disponible = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Repartidor'
        verbose_name_plural = 'Repartidores'

    def __str__(self):
        return self.user.get_username()


class Pedido(models.Model):
    ESTADOS = [
        ('registrado', 'Registrado'),
        ('asignado', 'Asignado'),
        ('retirado', 'Retirado'),
        ('en_viaje', 'En viaje'),
        ('entregado', 'Entregado'),
        ('fallido', 'Fallido'),
        ('cancelado', 'Cancelado'),
    ]

    TRANSICIONES_PERMITIDAS = {
        'registrado': ['asignado', 'cancelado'],
        'asignado': ['retirado', 'cancelado'],
        'retirado': ['en_viaje'],
        'en_viaje': ['entregado', 'fallido'],
        'entregado': [],
        'fallido': [],
        'cancelado': [],
    }

    LONGITUD_CODIGO = 20
    INTENTOS_CODIGO = 5

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    clave_idempotencia = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
        editable=False
    )

    comercio = models.ForeignKey(
        'operario.Comercio',
        on_delete=models.PROTECT,
        related_name='pedidos',
        null=True,
        blank=True
    )

    direccion_destino = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )

    especificaciones_traslado = models.TextField(
        blank=True,
        default=''
    )

    fecha_hora_estimada_entrega = models.DateTimeField(
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='registrado'
    )

    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos_asignados',
        null=True,
        blank=True
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

    @classmethod
    def generar_codigo(cls):
        """Genera un código de seguimiento alfanumérico impredecible."""
        caracteres = string.ascii_uppercase + string.digits
        return ''.join(
            secrets.choice(caracteres)
            for _ in range(cls.LONGITUD_CODIGO)
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
        ordering = ['fecha', 'pk']

    def __str__(self):
        return f'{self.pedido.codigo}: {self.estado_nuevo}'
