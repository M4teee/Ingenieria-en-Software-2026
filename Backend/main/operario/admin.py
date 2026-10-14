from django.contrib import admin
from main.users.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

admin.site.unregister(Group)
admin.site.site_header = 'Panel de operario'
admin.site.site_title = 'Pedidos Martin'
admin.site.index_title = 'Inicio'
admin.site.site_url = None

# Crea tu clase de administración extendiendo la de Django
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('vehiculo',)
    list_select_related = ('vehiculo',)
    list_filter = UserAdmin.list_filter + ('vehiculo',)

    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {'fields': ('vehiculo',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos adicionales', {'fields': ('vehiculo',)}),
    )
