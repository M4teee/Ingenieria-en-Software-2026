# main\operario\models.py

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