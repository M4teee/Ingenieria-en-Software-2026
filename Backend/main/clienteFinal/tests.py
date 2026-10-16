from datetime import datetime, timezone as datetime_timezone

from django.test import TestCase, override_settings
from django.urls import reverse

from main.operario.models import Comercio
from main.repartidor.models import HistorialEstado, Pedido
from main.users.models import User
from .views import ESTADOS, debe_mostrar_tiempo


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class SeguimientoPersistidoTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='cliente_final_test',
            password='test1234',
        )
        self.comercio = Comercio.objects.create(
            nombre='Comercio de prueba',
            direccion='Calle 1',
            contacto='contacto@example.test',
        )
        self.pedido = Pedido.objects.create(
            codigo='ABC123XYZ789',
            comercio=self.comercio,
            direccion_destino='Calle 2',
            especificaciones_traslado='Frágil',
            fecha_hora_estimada_entrega=datetime(
                2026, 10, 15, 19, 30, tzinfo=datetime_timezone.utc
            ),
            estado='en_viaje',
        )
        HistorialEstado.objects.create(
            pedido=self.pedido,
            estado_nuevo='registrado',
            usuario=self.usuario,
        )

    def test_muestra_estado_comercio_y_estimacion_del_pedido_persistido(self):
        respuesta = self.client.get(
            reverse('seguimiento', args=[self.pedido.codigo])
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'En viaje')
        self.assertContains(respuesta, 'Comercio de prueba')
        self.assertContains(respuesta, '16:30')
        self.assertContains(respuesta, 'Registrado')

    def test_no_muestra_estimacion_antes_del_estado_en_viaje(self):
        self.pedido.estado = 'registrado'
        self.pedido.save(update_fields=['estado'])

        respuesta = self.client.get(
            reverse('seguimiento', args=[self.pedido.codigo])
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, 'Llegada estimada')

    def test_no_muestra_estimacion_en_estados_finales(self):
        for estado in ('entregado', 'fallido', 'cancelado'):
            with self.subTest(estado=estado):
                self.pedido.estado = estado
                self.pedido.save(update_fields=['estado'])
                respuesta = self.client.get(
                    reverse('seguimiento', args=[self.pedido.codigo])
                )
                self.assertEqual(respuesta.status_code, 200)
                self.assertNotContains(respuesta, 'Llegada estimada')

    def test_codigo_inexistente_devuelve_404(self):
        respuesta = self.client.get(reverse('seguimiento', args=['NO-EXISTE']))

        self.assertEqual(respuesta.status_code, 404)

    def test_regla_de_visibilidad_de_la_estimacion(self):
        self.assertTrue(debe_mostrar_tiempo('en_viaje', self.pedido.fecha_hora_estimada_entrega))
        self.assertFalse(debe_mostrar_tiempo('en_viaje', None))
        self.assertFalse(debe_mostrar_tiempo('entregado', self.pedido.fecha_hora_estimada_entrega))

    def test_consulta_es_solo_lectura_get(self):
        respuesta = self.client.post(
            reverse('seguimiento', args=[self.pedido.codigo])
        )

        self.assertEqual(respuesta.status_code, 405)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'en_viaje')

    def test_historial_persistido_se_muestra_en_orden_cronologico(self):
        posterior = HistorialEstado.objects.create(
            pedido=self.pedido,
            estado_anterior='registrado',
            estado_nuevo='asignado',
            usuario=self.usuario,
        )
        anterior = HistorialEstado.objects.create(
            pedido=self.pedido,
            estado_anterior='asignado',
            estado_nuevo='en_viaje',
            usuario=self.usuario,
        )
        HistorialEstado.objects.filter(pedido=self.pedido, estado_nuevo='registrado').update(
            fecha=datetime(2026, 10, 15, 16, 0, tzinfo=datetime_timezone.utc)
        )
        HistorialEstado.objects.filter(pk=posterior.pk).update(
            fecha=datetime(2026, 10, 15, 17, 0, tzinfo=datetime_timezone.utc)
        )
        HistorialEstado.objects.filter(pk=anterior.pk).update(
            fecha=datetime(2026, 10, 15, 18, 0, tzinfo=datetime_timezone.utc)
        )

        respuesta = self.client.get(
            reverse('seguimiento', args=[self.pedido.codigo])
        )

        self.assertEqual(respuesta.status_code, 200)
        eventos = list(respuesta.context['historial'])
        self.assertEqual(
            [evento['etiqueta'] for evento in eventos],
            ['Registrado', 'Asignado', 'En viaje'],
        )
        self.assertEqual(eventos[-1]['etiqueta'], ESTADOS[self.pedido.estado][0])
        self.assertEqual(
            set(eventos[0]),
            {'etiqueta', 'clase', 'fecha'},
        )
        self.assertNotContains(respuesta, 'contacto@example.test')
        self.assertNotContains(respuesta, 'Frágil')

    def test_evento_de_auditoria_sin_transicion_no_duplica_estado_en_timeline(self):
        HistorialEstado.objects.create(
            pedido=self.pedido,
            estado_anterior='asignado',
            estado_nuevo='asignado',
            usuario=self.usuario,
            incidencia='Aceptado por repartidor',
        )

        respuesta = self.client.get(reverse('seguimiento', args=[self.pedido.codigo]))

        eventos = list(respuesta.context['historial'])
        self.assertEqual(len(eventos), 1)
        self.assertEqual(eventos[0]['etiqueta'], 'Registrado')
