# main\operario\models.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

class Comercio(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    direccion = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Comercio'
        verbose_name_plural = 'Comercios'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class DevolucionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError('La confirmación de devolución es inmutable.')

    def delete(self):
        raise ValidationError('La confirmación de devolución es inmutable.')


class Devolucion(models.Model):
    pedido = models.OneToOneField(
        'repartidor.Pedido',
        on_delete=models.PROTECT,
        related_name='devolucion_confirmada',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='devoluciones_confirmadas',
    )
    fecha = models.DateTimeField(auto_now_add=True)

    objects = DevolucionQuerySet.as_manager()

    class Meta:
        verbose_name = 'Devolución confirmada'
        verbose_name_plural = 'Devoluciones confirmadas'
        ordering = ['fecha', 'pk']

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError('La confirmación de devolución es inmutable.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('La confirmación de devolución es inmutable.')

    def __str__(self):
        return f'{self.pedido.codigo}: devolución registrada'
