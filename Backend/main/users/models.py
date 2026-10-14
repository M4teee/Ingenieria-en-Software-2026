# main\users\models.py

from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    vehiculo = models.ForeignKey(
        'users.Vehiculo',
        on_delete= models.PROTECT,
        related_name='usuarios',
        null=True,
        blank=True
    )
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

class Vehiculo(models.Model):
    name = models.CharField(max_length=30)
    # usuarios = models.ManyToManyField(User, related_name='vehiculos') # Esto está mal. Cada usuario solo debería poder tener un vehículo, no varios 

    def __str__(self):
        return self.name