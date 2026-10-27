from django.contrib import admin

from main.users.models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
