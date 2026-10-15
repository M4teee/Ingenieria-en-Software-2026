# main/repartidor/models.py

from django.db import models

class Repartidor(models.Model):
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='repartidor',
    )
    pin = models.CharField(max_length=6, unique=True)
    disponible = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Repartidor'
        verbose_name_plural = 'Repartidores'

    def __str__(self):
        return self.user.get_username()
