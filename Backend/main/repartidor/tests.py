from django.test import TestCase, override_settings

from main.users.models import User
from .models import Pedido, Repartidor


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class PedidoTransicionesTests(TestCase):

    def setUp(self):
        self.repartidor = User.objects.create_user(
            username='repartidor_test',
            password='test1234'
        )

        self.pedido = Pedido.objects.create(
            codigo='TEST-001',
            repartidor=self.repartidor,
            estado='asignado'
        )

    def test_asignado_puede_pasar_a_retirado(self):
        self.assertTrue(
            self.pedido.puede_cambiar_a('retirado')
        )

    def test_asignado_no_puede_pasar_directamente_a_entregado(self):
        self.assertFalse(
            self.pedido.puede_cambiar_a('entregado')
        )

    def test_retirado_puede_pasar_a_en_viaje(self):
        self.pedido.estado = 'retirado'

        self.assertTrue(
            self.pedido.puede_cambiar_a('en_viaje')
        )

    def test_en_viaje_puede_pasar_a_entregado(self):
        self.pedido.estado = 'en_viaje'

        self.assertTrue(
            self.pedido.puede_cambiar_a('entregado')
        )

    def test_en_viaje_puede_pasar_a_fallido(self):
        self.pedido.estado = 'en_viaje'

        self.assertTrue(
            self.pedido.puede_cambiar_a('fallido')
        )

    def test_entregado_es_estado_final(self):
        self.pedido.estado = 'entregado'

        self.assertFalse(
            self.pedido.puede_cambiar_a('en_viaje')
        )

    def test_fallido_es_estado_final(self):
        self.pedido.estado = 'fallido'

        self.assertFalse(
            self.pedido.puede_cambiar_a('entregado')
        )

    def test_registrado_puede_asignarse_o_cancelarse(self):
        self.pedido.estado = 'registrado'

        self.assertTrue(self.pedido.puede_cambiar_a('asignado'))
        self.assertTrue(self.pedido.puede_cambiar_a('cancelado'))
        self.assertFalse(self.pedido.puede_cambiar_a('retirado'))

    def test_asignado_puede_cancelarse_antes_del_retiro(self):
        self.pedido.estado = 'asignado'

        self.assertTrue(self.pedido.puede_cambiar_a('cancelado'))

    def test_pedido_retirado_no_puede_cancelarse(self):
        self.pedido.estado = 'retirado'

        self.assertFalse(self.pedido.puede_cambiar_a('cancelado'))

    def test_pedido_nuevo_puede_persistirse_sin_repartidor(self):
        pedido = Pedido.objects.create(codigo='TEST-SIN-REPARTIDOR')

        self.assertIsNone(pedido.repartidor)
        self.assertEqual(pedido.estado, 'registrado')


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ActualizarEstadoTests(TestCase):

    def setUp(self):
        self.repartidor = User.objects.create_user(
            username='repartidor_vista',
            password='test1234'
        )

        self.client.login(
            username='repartidor_vista',
            password='test1234'
        )

        self.pedido = Pedido.objects.create(
            codigo='TEST-VISTA-001',
            repartidor=self.repartidor,
            estado='asignado'
        )

    def test_actualizar_a_retirado_crea_historial(self):
        respuesta = self.client.post(
            f'/repartidor/pedido/{self.pedido.id}/actualizar-estado/',
            {
                'estado': 'retirado'
            }
        )

        self.pedido.refresh_from_db()

        self.assertEqual(
            self.pedido.estado,
            'retirado'
        )

        self.assertEqual(
            self.pedido.historial.count(),
            1
        )

        historial = self.pedido.historial.first()

        self.assertEqual(
            historial.estado_anterior,
            'asignado'
        )

        self.assertEqual(
            historial.estado_nuevo,
            'retirado'
        )

        self.assertEqual(
            historial.usuario,
            self.repartidor
        )

        self.assertEqual(
            respuesta.status_code,
            302
        )

    def test_entregado_libera_al_repartidor(self):
        self.pedido.estado = 'en_viaje'
        self.pedido.save()

        self.client.post(
            f'/repartidor/pedido/{self.pedido.id}/actualizar-estado/',
            {
                'estado': 'entregado'
            }
        )

        self.pedido.refresh_from_db()

        self.assertEqual(
            self.pedido.estado,
            'entregado'
        )

        self.assertTrue(
            self.repartidor.disponible
        )

    def test_fallido_registra_incidencia(self):
        self.pedido.estado = 'en_viaje'
        self.pedido.save()

        self.client.post(
            f'/repartidor/pedido/{self.pedido.id}/actualizar-estado/',
            {'estado': 'fallido'}
        )

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'fallido')
        historial = self.pedido.historial.first()
        self.assertEqual(historial.estado_nuevo, 'fallido')
        self.assertIn('Retornar el pedido al centro de distribución', historial.incidencia)
        self.assertTrue(self.repartidor.disponible)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class DisponibilidadRepartidorTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='repartidor_pin',
            password='test1234',
        )
        self.perfil = Repartidor.objects.create(
            user=self.user,
            pin='0123',
        )

    def test_login_pin_valido_autentica_al_repartidor(self):
        response = self.client.post('/repartidor/login-pin/', {'pin': '0123'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_pin_invalido_muestra_mensaje_de_historia(self):
        response = self.client.post('/repartidor/login-pin/', {'pin': '9999'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PIN incorrecto. Verifique los dígitos')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_pin_de_mas_de_cuatro_digitos_no_autentica(self):
        response = self.client.post('/repartidor/login-pin/', {'pin': '000123'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_toggle_disponibilidad_persiste_el_estado(self):
        self.client.force_login(self.user)

        response = self.client.post('/repartidor/disponibilidad/')

        self.perfil.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.perfil.disponible)
        self.assertTrue(self.user.disponible)

    def test_toggle_rechaza_disponibilidad_con_pedido_activo(self):
        self.client.force_login(self.user)
        self.perfil.disponible = False
        self.perfil.save(update_fields=['disponible'])
        Pedido.objects.create(
            codigo='ACTIVE-001',
            repartidor=self.user,
            estado='asignado',
        )

        self.client.post('/repartidor/disponibilidad/')

        self.perfil.refresh_from_db()
        self.assertFalse(self.perfil.disponible)
