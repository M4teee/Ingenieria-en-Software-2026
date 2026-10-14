from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
# from .models import Vehiculo  # Importa tu modelo de Vehiculo

# 1. Quita el registro por defecto del modelo User
admin.site.unregister(User)

# 2. Crea tu clase de administración extendiendo la de Django
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Agrega el nombre del método personalizado en la lista de columnas visibles
    list_display = UserAdmin.list_display + ('mostrar_vehiculos',)

    # Optimiza la consulta SQL cargando los datos relacionados de antemano (Evita el problema N+1)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('vehiculos') # 'vehiculos' es el related_name del ManyToMany

    # 3. Define el método para extraer y formatear los datos de la relación ManyToMany
    def mostrar_vehiculos(self, obj):
        # Retorna un string con todas las patentes o nombres de los vehículos separados por comas
        return ", ". join([vehiculo.name for vehiculo in obj.vehiculos.all()])
    
    # Define el título que tendrá la columna en la interfaz del admin
    mostrar_vehiculos.short_description = 'Vehículos Asignados'