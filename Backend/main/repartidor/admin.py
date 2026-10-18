from django.contrib import admin
from .models import Repartidor

@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ('user', 'pin', 'disponible', 'vehiculo')
    search_fields = ('user__username', 'pin', 'vehiculo')
