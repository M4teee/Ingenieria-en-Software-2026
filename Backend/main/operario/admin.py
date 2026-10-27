from django.contrib import admin
from main.users.models import User
from main.operario.models import Comercio
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

admin.site.unregister(Group)
admin.site.site_header = 'Administración'
admin.site.index_title = 'Inicio'
admin.site.site_url = None


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Permisos del SGR', {'fields': ('is_operario',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Permisos del SGR', {'fields': ('is_operario',)}),
    )
    list_display = UserAdmin.list_display + ('is_operario',)
    list_filter = UserAdmin.list_filter + ('is_operario',)

@admin.register(Comercio)
class ComercioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'contacto', 'fecha_creacion', 'activo')
    search_fields = ('nombre', 'direccion', 'contacto', 'activo')
    list_filter = ('fecha_creacion',)
    readonly_fields = ('fecha_creacion',)
    date_hierarchy = 'fecha_creacion'
