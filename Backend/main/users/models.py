# main/users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser


class Vehiculo(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class User(AbstractUser):
    is_operario = models.BooleanField(
        default=False,
        verbose_name='operario',
        help_text='Designa si el usuario puede acceder al módulo de operario.',
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

