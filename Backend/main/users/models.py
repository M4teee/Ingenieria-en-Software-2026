from django.db import models
from django.contrib.auth.models import User

class Vehiculo(models.Model):
    name = models.CharField(max_length=30)
    usuarios = models.ManyToManyField(User, related_name='vehiculos')

    def __str__(self):
        return self.name