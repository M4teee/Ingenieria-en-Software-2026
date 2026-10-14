# main\operario\models.py

from django.db import models

class Comercio(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)
    contacto = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
