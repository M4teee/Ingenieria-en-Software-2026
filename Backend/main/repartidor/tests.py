from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from main.operario.models import Comercio
from main.users.models import User
from .models import HistorialEstado, Pedido, Repartidor


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
class AsignacionConRespuestaTests(TestCase):

    def setUp(self):
        self.comercio = Comercio.objects.create(
            nombre='Comercio HU18', direccion='Calle 100', contacto='111222333',
        )
        self.user = User.objects.create_user(
            username='repartidor_hu18', password='test1234',
            first_name='Ana', last_name='Pérez',
        )
        self.perfil = Repartidor.objects.create(
            user=self.user, pin='4321', disponible=True,
        )
        self.client.force_login(self.user)

    def crear_pedido_asignado(self, segundos=0):
        from datetime import timedelta

        return Pedido.objects.create(
            codigo='HU18-TEST-001',
            comercio=self.comercio,
            estado='asignado',
            repartidor=self.user,
            fecha_hora_asignacion=timezone.now() - timedelta(seconds=segundos),
        )

    def test_aceptar_confirma_y_detiene_temporizador_sin_marcar_retirado(self):
        pedido = self.crear_pedido_asignado(segundos=60)

        response = self.client.post(reverse('repartidor_aceptar', args=[pedido.pk]))

        pedido.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(pedido.estado, 'asignado')
        self.assertIsNone(pedido.fecha_hora_asignacion)
        self.assertIsNotNone(pedido.fecha_hora_aceptacion)
        self.assertEqual(pedido.repartidor, self.user)
        self.assertTrue(
            pedido.historial.filter(incidencia__contains='Aceptado por repartidor Ana Pérez').exists()
        )

    def test_aceptacion_habilita_la_accion_existente_de_retiro(self):
        pedido = self.crear_pedido_asignado()
        self.client.post(reverse('repartidor_aceptar', args=[pedido.pk]))

        response = self.client.get(reverse('repartidor'))

        self.assertContains(response, 'Marcar como Retirado')
        self.assertNotContains(response, 'Aceptar viaje')

    def test_rechazo_libera_pedido_y_registra_historial_de_estado(self):
        pedido = self.crear_pedido_asignado()

        response = self.client.post(reverse('repartidor_rechazar', args=[pedido.pk]))

        pedido.refresh_from_db()
        self.perfil.refresh_from_db()
        historial = HistorialEstado.objects.get(pedido=pedido)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(pedido.estado, 'registrado')
        self.assertIsNone(pedido.repartidor)
        self.assertEqual(historial.estado_anterior, 'asignado')
        self.assertEqual(historial.estado_nuevo, 'registrado')
        self.assertEqual(historial.usuario, self.user)
        self.assertEqual(historial.incidencia, 'Rechazado por repartidor Ana Pérez')
        self.assertFalse(self.perfil.disponible)

    def test_expiracion_en_home_libera_pedido_y_registra_evento(self):
        pedido = self.crear_pedido_asignado(segundos=301)

        response = self.client.get(reverse('repartidor'))

        pedido.refresh_from_db()
        self.perfil.refresh_from_db()
        self.assertContains(response, 'El tiempo de espera se agotó')
        self.assertEqual(pedido.estado, 'registrado')
        self.assertIsNone(pedido.repartidor)
        self.assertFalse(self.perfil.disponible)
        self.assertIn('expiración', pedido.historial.get().incidencia)

    def test_aceptar_al_limite_de_300_segundos_libera_pedido(self):
        pedido = self.crear_pedido_asignado(segundos=300)

        self.client.post(reverse('repartidor_aceptar', args=[pedido.pk]))

        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'registrado')
        self.assertIsNone(pedido.repartidor)

    def test_aceptar_requiere_post_y_asignacion_al_usuario(self):
        pedido = self.crear_pedido_asignado()
        self.assertEqual(
            self.client.get(reverse('repartidor_aceptar', args=[pedido.pk])).status_code,
            405,
        )

        otro = User.objects.create_user(username='otro_hu18', password='x')
        self.client.force_login(otro)
        response = self.client.post(reverse('repartidor_aceptar', args=[pedido.pk]))

        self.assertEqual(response.status_code, 400)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'asignado')

    def test_no_se_libera_un_pedido_por_el_endpoint_de_avance_de_estado(self):
        pedido = self.crear_pedido_asignado()

        self.client.post(
            reverse('actualizar_estado', args=[pedido.pk]),
            {'estado': 'registrado'},
        )

        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'asignado')
        self.assertEqual(pedido.repartidor, self.user)
