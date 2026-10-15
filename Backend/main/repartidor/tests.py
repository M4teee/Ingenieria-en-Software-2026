from django.test import TestCase

from main.users.models import User
from .models import Pedido


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

        historial = self.pedido.historial.first()

        self.assertEqual(
            historial.estado_anterior,
            'en_viaje'
        )

        self.assertEqual(
            historial.estado_nuevo,
            'entregado'
        )

    def test_fallido_registra_incidencia(self):
        self.pedido.estado = 'en_viaje'
        self.pedido.save()

        self.client.post(
            f'/repartidor/pedido/{self.pedido.id}/actualizar-estado/',
            {
                'estado': 'fallido'
            }
        )

        self.pedido.refresh_from_db()

        self.assertEqual(
            self.pedido.estado,
            'fallido'
        )

        historial = self.pedido.historial.first()

        self.assertEqual(
            historial.estado_nuevo,
            'fallido'
        )

        self.assertIn(
            'Retornar el pedido al centro de distribución',
            historial.incidencia
        )

        self.assertTrue(
            self.repartidor.disponible
        )