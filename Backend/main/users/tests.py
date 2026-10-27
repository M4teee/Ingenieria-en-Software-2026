from django.test import TestCase

# Create your tests here.
from django.contrib import admin
from django.test import RequestFactory, TestCase
from django.urls import reverse

from main.operario.models import Comercio
from main.repartidor.models import HistorialEstado, Pedido, Repartidor
from main.users.models import User, Vehiculo


class ModelosPropiosEnAdminTests(TestCase):
    def setUp(self):
        self.administrador = User.objects.create_superuser(
            username='admin_modelos', password='clave-prueba',
        )
        self.client.force_login(self.administrador)

    def test_todos_los_modelos_propios_estan_registrados_y_listados(self):
        modelos = (User, Vehiculo, Comercio, Pedido, HistorialEstado, Repartidor)
        for modelo in modelos:
            with self.subTest(modelo=modelo.__name__):
                self.assertIn(modelo, admin.site._registry)

        respuesta = self.client.get(reverse('admin:index'))
        self.assertEqual(respuesta.status_code, 200)
        for nombre_url in (
            'admin:users_user_changelist',
            'admin:users_vehiculo_changelist',
            'admin:operario_comercio_changelist',
            'admin:repartidor_pedido_changelist',
            'admin:repartidor_historialestado_changelist',
            'admin:repartidor_repartidor_changelist',
        ):
            with self.subTest(url=nombre_url):
                self.assertContains(respuesta, reverse(nombre_url))

    def test_pedido_e_historial_se_pueden_consultar_pero_no_alterar(self):
        request = RequestFactory().get('/admin/')
        request.user = self.administrador

        for modelo in (Pedido, HistorialEstado):
            with self.subTest(modelo=modelo.__name__):
                model_admin = admin.site._registry[modelo]
                self.assertTrue(model_admin.has_view_permission(request))
                self.assertFalse(model_admin.has_add_permission(request))
                self.assertFalse(model_admin.has_change_permission(request))
                self.assertFalse(model_admin.has_delete_permission(request))
