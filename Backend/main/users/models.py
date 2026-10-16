# main/users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    vehiculo = models.ForeignKey(
        'users.Vehiculo',
        on_delete=models.PROTECT,
        related_name='usuarios',
        null=True,
        blank=True
    )

    @property
    def disponible(self):
        tiene_pedido_activo = self.pedidos_asignados.filter(
            estado__in=['asignado', 'retirado', 'en_viaje']
        ).exists()
        try:
            disponibilidad_declarada = self.repartidor.disponible
        except User.repartidor.RelatedObjectDoesNotExist:
            disponibilidad_declarada = True
        return disponibilidad_declarada and not tiene_pedido_activo

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class Vehiculo(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
