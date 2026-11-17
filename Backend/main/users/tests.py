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


class SimpleConnectionPoolTests(TestCase):
    def setUp(self):
        from config.pool import SimpleConnectionPool
        self.pool_class = SimpleConnectionPool

    def test_pool_descarta_conexiones_con_inactividad_mayor_a_max_idle_seconds(self):
        pool = self.pool_class(max_idle_seconds=20.0, open=True)

        class MockConn:
            def __init__(self):
                self.closed = False
                self.broken = False
                self.close_called = False

            def close(self):
                self.closed = True
                self.close_called = True

            def fileno(self):
                return -1

        conn_expirada = MockConn()
        # Encolamos la conexión simulando que fue retornada hace 25 segundos
        import time
        pool._pool.put_nowait((conn_expirada, time.monotonic() - 25.0))

        # Intentamos obtener conexión del pool; como está expirada (>20s), debe cerrarse
        # y no ser reutilizada
        self.assertEqual(pool._pool.qsize(), 1)
        # Mock de connect para no abrir conexión real
        import psycopg
        conn_fresca = MockConn()
        original_connect = psycopg.connect
        psycopg.connect = lambda *a, **kw: conn_fresca
        try:
            conn_obtenida = pool.getconn()
            self.assertTrue(conn_expirada.close_called)
            self.assertIs(conn_obtenida, conn_fresca)
        finally:
            psycopg.connect = original_connect

    def test_pool_reutiliza_conexion_activa_dentro_de_max_idle(self):
        pool = self.pool_class(max_idle_seconds=20.0, open=True)

        class MockConn:
            def __init__(self):
                self.closed = False
                self.broken = False
                self.close_called = False

            def close(self):
                self.closed = True
                self.close_called = True

            def fileno(self):
                return -1

        conn_valida = MockConn()
        import time
        pool._pool.put_nowait((conn_valida, time.monotonic() - 5.0))

        conn_obtenida = pool.getconn()
        self.assertIs(conn_obtenida, conn_valida)
        self.assertFalse(conn_valida.close_called)

    def test_pool_descarta_conexion_cerrada_o_rota(self):
        pool = self.pool_class(max_idle_seconds=20.0, open=True)

        class MockConn:
            def __init__(self, closed=False, broken=False):
                self.closed = closed
                self.broken = broken
                self.close_called = False

            def close(self):
                self.closed = True
                self.close_called = True

            def fileno(self):
                return -1

        conn_rota = MockConn(broken=True)
        import time
        pool._pool.put_nowait((conn_rota, time.monotonic() - 2.0))

        import psycopg
        conn_fresca = MockConn()
        original_connect = psycopg.connect
        psycopg.connect = lambda *a, **kw: conn_fresca
        try:
            conn_obtenida = pool.getconn()
            self.assertTrue(conn_rota.close_called)
            self.assertIs(conn_obtenida, conn_fresca)
        finally:
            psycopg.connect = original_connect

