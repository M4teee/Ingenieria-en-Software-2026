# main/users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # No tiene sentido hacer un modelo Vehiculo a parte. Debería ser un campo mas tipo CHOICES en Usuario
    vehiculo = models.ForeignKey(
        'users.Vehiculo',
        on_delete=models.PROTECT,
        related_name='usuarios',
        null=True,
        blank=True
    )

    @property
    def disponible(self):
        return not self.pedidos_asignados.filter(
            estado__in=['asignado', 'retirado', 'en_viaje']
        ).exists()

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class Vehiculo(models.Model): # No tiene sentido hacer un modelo Vehiculo. Debería ser un campo mas tipo CHOICES en Usuario
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name