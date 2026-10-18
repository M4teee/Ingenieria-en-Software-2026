from uuid import UUID
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse

from main.operario.models import Comercio
from main.repartidor.models import HistorialEstado, Pedido
from main.repartidor.models import Repartidor
from main.users.models import User


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class CargarPedidoTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_test',
            password='test1234',
            is_staff=True,
        )
        self.no_staff = User.objects.create_user(
            username='usuario_test',
            password='test1234',
        )
        self.comercio = Comercio.objects.create(
            nombre='Comercio activo',
            direccion='Av. Siempre Viva 123',
            contacto='comercio@example.test',
        )
        self.url = reverse('operario:cargar_pedido')
        self.client.force_login(self.operario)

    def _datos_formulario(self, **cambios):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        datos = {
            'clave_idempotencia': str(
                respuesta.context['form']['clave_idempotencia'].value()
            ),
            'comercio': str(self.comercio.pk),
            'direccion_destino': 'Calle Destino 456',
            'especificaciones_traslado': 'Manipular con cuidado',
            'fecha_hora_estimada_entrega': '2026-10-16T15:45',
        }
        datos.update(cambios)
        return datos

    def test_usuario_anonimo_es_redirigido_al_login(self):
        self.client.logout()

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login/', respuesta.url)

    def test_usuario_autenticado_sin_is_staff_recibe_403(self):
        self.client.force_login(self.no_staff)

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 403)

    def test_alta_crea_pedido_historial_y_muestra_codigo(self):
        datos = self._datos_formulario()

        respuesta = self.client.post(self.url, datos)

        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get()
        self.assertEqual(respuesta.url, reverse(
            'operario:pedido_registrado', args=[pedido.pk]
        ))
        self.assertEqual(pedido.estado, 'registrado')
        self.assertIsNone(pedido.repartidor)
        self.assertEqual(pedido.comercio, self.comercio)
        self.assertEqual(pedido.direccion_destino, 'Calle Destino 456')
        self.assertEqual(pedido.especificaciones_traslado, 'Manipular con cuidado')
        self.assertEqual(
            timezone.localtime(
                pedido.fecha_hora_estimada_entrega
            ).strftime('%Y-%m-%dT%H:%M'),
            '2026-10-16T15:45',
        )
        self.assertRegex(pedido.codigo, r'^[A-Z0-9]{20}$')
        self.assertEqual(UUID(datos['clave_idempotencia']), pedido.clave_idempotencia)

        evento = HistorialEstado.objects.get(pedido=pedido)
        self.assertEqual(evento.estado_nuevo, 'registrado')
        self.assertEqual(evento.estado_anterior, '')
        self.assertEqual(evento.usuario, self.operario)

        confirmacion = self.client.get(respuesta.url)
        self.assertEqual(confirmacion.status_code, 200)
        self.assertContains(confirmacion, 'Pedido registrado con éxito')
        self.assertContains(confirmacion, pedido.codigo)
        self.assertContains(confirmacion, 'navigator.clipboard')

    def test_comercio_inactivo_rechaza_alta_con_mensaje_de_historia(self):
        self.comercio.activo = False
        self.comercio.save(update_fields=['activo'])

        respuesta = self.client.post(
            self.url,
            self._datos_formulario(),
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(
            respuesta,
            'El comercio seleccionado se encuentra inhabilitado para nuevos pedidos',
        )
        self.assertFalse(Pedido.objects.exists())


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class PanelOperarioTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='panel_operario', password='test1234', is_staff=True,
        )
        self.usuario_comun = User.objects.create_user(
            username='panel_comun', password='test1234',
        )
        self.comercio = Comercio.objects.create(
            nombre='Panel Comercio', direccion='Calle 10', contacto='111',
        )
        self.pedido = Pedido.objects.create(
            codigo='PANEL-001', comercio=self.comercio,
            direccion_destino='Destino 10', estado='registrado',
        )
        self.client.force_login(self.operario)

    def test_panel_lista_pedido_y_detalle_muestra_historial(self):
        HistorialEstado.objects.create(
            pedido=self.pedido,
            estado_nuevo='registrado',
            usuario=self.operario,
        )

        lista = self.client.get(reverse('operario:inicio'))
        detalle = self.client.get(
            reverse('operario:detalle_pedido', args=[self.pedido.pk])
        )

        self.assertEqual(lista.status_code, 200)
        self.assertContains(lista, 'PANEL-001')
        self.assertContains(lista, 'Sin asignar')
        self.assertEqual(detalle.status_code, 200)
        self.assertContains(detalle, 'Historial del pedido')
        self.assertContains(detalle, 'Registrado')

    def test_usuario_sin_is_staff_no_accede_al_panel_ni_detalle(self):
        self.client.force_login(self.usuario_comun)

        self.assertEqual(self.client.get(reverse('operario:inicio')).status_code, 403)
        self.assertEqual(
            self.client.get(reverse('operario:detalle_pedido', args=[self.pedido.pk])).status_code,
            403,
        )

    def test_asignar_disponible_cambia_estado_y_registra_evento(self):
        usuario_repartidor = User.objects.create_user(
            username='repartidor_disponible', first_name='Rosa', password='test1234',
        )
        perfil = Repartidor.objects.create(
            user=usuario_repartidor, pin='1111', disponible=True,
        )

        respuesta = self.client.post(
            reverse('operario:asignar_repartidor', args=[self.pedido.pk]),
            {'repartidor': perfil.pk},
        )

        self.pedido.refresh_from_db()
        evento = HistorialEstado.objects.get(pedido=self.pedido)
        self.assertRedirects(
            respuesta,
            reverse('operario:detalle_pedido', args=[self.pedido.pk]),
        )
        self.assertEqual(self.pedido.estado, 'asignado')
        self.assertEqual(self.pedido.repartidor, usuario_repartidor)
        self.assertIsNotNone(self.pedido.fecha_hora_asignacion)
        self.assertEqual(evento.estado_anterior, 'registrado')
        self.assertEqual(evento.estado_nuevo, 'asignado')
        self.assertEqual(evento.usuario, self.operario)

    def test_pedido_no_se_asigna_a_repartidor_inactivo(self):
        usuario_repartidor = User.objects.create_user(
            username='repartidor_inactivo', password='test1234', is_active=False,
        )
        perfil = Repartidor.objects.create(
            user=usuario_repartidor, pin='2222', disponible=True,
        )

        respuesta = self.client.post(
            reverse('operario:asignar_repartidor', args=[self.pedido.pk]),
            {'repartidor': perfil.pk},
        )

        self.pedido.refresh_from_db()
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(self.pedido.estado, 'registrado')
        self.assertIsNone(self.pedido.repartidor)
        self.assertFalse(HistorialEstado.objects.exists())

    def test_asignar_requiere_post(self):
        respuesta = self.client.get(
            reverse('operario:asignar_repartidor', args=[self.pedido.pk])
        )

        self.assertEqual(respuesta.status_code, 405)
        self.assertFalse(HistorialEstado.objects.exists())


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class CargarPedidoValidacionesTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_validaciones', password='test1234', is_staff=True,
        )
        self.comercio = Comercio.objects.create(
            nombre='Comercio validaciones',
            direccion='Av. Siempre Viva 123',
            contacto='comercio@example.test',
        )
        self.url = reverse('operario:cargar_pedido')
        self.client.force_login(self.operario)

    def _datos_formulario(self, **cambios):
        respuesta = self.client.get(self.url)
        return {
            'clave_idempotencia': str(
                respuesta.context['form']['clave_idempotencia'].value()
            ),
            'comercio': str(self.comercio.pk),
            'direccion_destino': 'Calle Destino 456',
            'especificaciones_traslado': 'Manipular con cuidado',
            'fecha_hora_estimada_entrega': '2026-10-16T15:45',
            **cambios,
        }

    def test_campos_obligatorios_y_fecha_invalida_no_crean_pedido(self):
        datos = self._datos_formulario(
            direccion_destino='',
            especificaciones_traslado='',
            fecha_hora_estimada_entrega='fecha-invalida',
        )

        respuesta = self.client.post(self.url, datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].errors)
        self.assertFalse(Pedido.objects.exists())

    def test_reenvio_con_misma_clave_es_idempotente(self):
        datos = self._datos_formulario()

        primera = self.client.post(self.url, datos)
        segunda = self.client.post(self.url, datos)

        self.assertEqual(primera.status_code, 302)
        self.assertEqual(segunda.status_code, 302)
        self.assertEqual(segunda.url, primera.url)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(HistorialEstado.objects.count(), 1)

    def test_colision_de_codigo_se_reintenta(self):
        Pedido.objects.create(codigo='CODIGO-COLISION')

        with patch.object(
            Pedido,
            'generar_codigo',
            side_effect=['CODIGO-COLISION', 'CODIGO-UNICO-12345'],
        ):
            respuesta = self.client.post(self.url, self._datos_formulario())

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Pedido.objects.count(), 2)
        self.assertEqual(
            Pedido.objects.exclude(codigo='CODIGO-COLISION').get().codigo,
            'CODIGO-UNICO-12345',
        )

    def test_fallo_al_crear_historial_revierte_pedido(self):
        with patch(
            'main.operario.views.HistorialEstado.objects.create',
            side_effect=IntegrityError('fallo simulado'),
        ):
            with self.assertRaises(IntegrityError):
                self.client.post(self.url, self._datos_formulario())

        self.assertFalse(Pedido.objects.exists())
        self.assertFalse(HistorialEstado.objects.exists())

    def test_comercio_que_se_inactiva_tras_validar_se_rechaza_en_servidor(self):
        from main.operario.forms import PedidoForm
        from main.operario.views import ComercioInactivoError, _crear_pedido

        datos = {
            'clave_idempotencia': 'd8f1acb1-8ad0-4e6c-9089-eec0ce74c041',
            'comercio': str(self.comercio.pk),
            'direccion_destino': 'Calle Destino 456',
            'especificaciones_traslado': 'Manipular con cuidado',
            'fecha_hora_estimada_entrega': '2026-10-16T15:45',
        }
        formulario = PedidoForm(data=datos)
        self.assertTrue(formulario.is_valid(), formulario.errors)
        self.comercio.activo = False
        self.comercio.save(update_fields=['activo'])

        with self.assertRaises(ComercioInactivoError):
            _crear_pedido(formulario, self.operario)

        self.assertFalse(Pedido.objects.exists())
