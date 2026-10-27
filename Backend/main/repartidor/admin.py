from django.contrib import admin

from .models import HistorialEstado, Pedido, Repartidor


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'comercio', 'estado', 'repartidor', 'fecha_creacion',
    )
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('codigo', 'comercio__nombre', 'repartidor__username')
    readonly_fields = ('fecha_creacion',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = (
        'pedido', 'estado_anterior', 'estado_nuevo', 'usuario', 'fecha',
    )
    list_filter = ('estado_nuevo', 'fecha')
    search_fields = ('pedido__codigo', 'usuario__username', 'incidencia')
    readonly_fields = (
        'pedido', 'estado_anterior', 'estado_nuevo', 'usuario', 'fecha',
        'fotografia', 'incidencia',
    )
    date_hierarchy = 'fecha'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Repartidor)
class RepartidorAdmin(admin.ModelAdmin):
    list_display = ('user', 'pin', 'disponible', 'vehiculo')
    search_fields = ('user__username', 'pin', 'vehiculo')
