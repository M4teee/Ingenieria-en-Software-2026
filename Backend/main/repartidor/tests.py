import shutil
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
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
        self.perfil = Repartidor.objects.create(
            user=self.repartidor, pin='1201', disponible=True,
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
        Repartidor.objects.create(user=otro, pin='6789')
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

    def test_login_pin_no_autentica_usuario_dado_de_baja(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        response = self.client.post('/repartidor/login-pin/', {'pin': '0123'})

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

    def test_usuario_autenticado_sin_perfil_no_accede_al_modulo(self):
        otro = User.objects.create_user(username='sin_perfil')
        self.client.force_login(otro)

        self.assertEqual(self.client.get(reverse('repartidor')).status_code, 403)
        self.assertEqual(
            self.client.post(reverse('repartidor_toggle_disponibilidad')).status_code,
            403,
        )


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class DetalleRepartidorTests(TestCase):
    def setUp(self):
        self.repartidor = User.objects.create_user(username='detalle_repartidor')
        Repartidor.objects.create(user=self.repartidor, pin='9876')
        self.otro_repartidor = User.objects.create_user(username='otro_detalle')
        Repartidor.objects.create(user=self.otro_repartidor, pin='9875')
        self.pedido = Pedido.objects.create(
            codigo='DETALLE-01', repartidor=self.repartidor,
            estado='entregado', direccion_destino='Destino privado',
            especificaciones_traslado='Contenido de prueba',
        )

    def test_repartidor_consulta_solo_sus_pedidos_y_su_historial(self):
        evento = HistorialEstado.objects.create(
            pedido=self.pedido, estado_nuevo='entregado', usuario=self.repartidor,
        )
        self.client.force_login(self.repartidor)

        response = self.client.get(
            reverse('repartidor_detalle_pedido', args=[self.pedido.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Destino privado')
        self.assertEqual(list(response.context['historial']), [evento])

        otro_pedido = Pedido.objects.create(
            codigo='DETALLE-02', repartidor=self.otro_repartidor, estado='entregado',
        )
        self.assertEqual(
            self.client.get(
                reverse('repartidor_detalle_pedido', args=[otro_pedido.pk])
            ).status_code,
            404,
        )

    def test_no_expone_detalle_completo_antes_de_aceptar_asignacion(self):
        from datetime import timedelta

        pedido = Pedido.objects.create(
            codigo='PENDIENTE-01', repartidor=self.repartidor, estado='asignado',
            fecha_hora_asignacion=timezone.now() - timedelta(seconds=10),
            direccion_destino='Destino antes de aceptar',
        )
        self.client.force_login(self.repartidor)

        response = self.client.get(
            reverse('repartidor_detalle_pedido', args=[pedido.pk])
        )

        self.assertRedirects(response, reverse('repartidor'))

    def test_no_puede_modificar_pedido_asignado_a_otro_repartidor(self):
        pedido_ajeno = Pedido.objects.create(
            codigo='AJENO-01',
            repartidor=self.otro_repartidor,
            estado='en_viaje',
        )
        self.client.force_login(self.repartidor)

        response = self.client.post(
            reverse('actualizar_estado', args=[pedido_ajeno.pk]),
            {'estado': 'entregado'},
        )

        pedido_ajeno.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(pedido_ajeno.estado, 'en_viaje')
        self.assertFalse(HistorialEstado.objects.filter(pedido=pedido_ajeno).exists())


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class FotografiasEntregaTests(TestCase):
    def setUp(self):
        self.directorio_media = tempfile.mkdtemp(prefix='sgr-test-media-')
        self.addCleanup(shutil.rmtree, self.directorio_media, ignore_errors=True)
        self.override_media = override_settings(MEDIA_ROOT=self.directorio_media)
        self.override_media.enable()
        self.addCleanup(self.override_media.disable)

        self.user = User.objects.create_user(username='foto_repartidor')
        self.perfil = Repartidor.objects.create(user=self.user, pin='1112')
        self.pedido = Pedido.objects.create(
            codigo='FOTO-01', repartidor=self.user, estado='en_viaje',
        )
        self.client.force_login(self.user)

    def _imagen(self):
        buffer = BytesIO()
        Image.new('RGB', (12, 12), color='red').save(buffer, format='PNG')
        return SimpleUploadedFile(
            'evidencia.png', buffer.getvalue(), content_type='image/png',
        )

    def test_foto_valida_se_comprime_y_persiste_con_estado_e_historial(self):
        response = self.client.post(
            reverse('actualizar_estado', args=[self.pedido.pk]),
            {'estado': 'entregado', 'fotografia': self._imagen()},
        )

        self.pedido.refresh_from_db()
        self.perfil.refresh_from_db()
        evento = HistorialEstado.objects.get(pedido=self.pedido)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.pedido.estado, 'entregado')
        self.assertTrue(evento.fotografia.name.endswith('.jpg'))
        self.assertTrue(evento.fotografia.storage.exists(evento.fotografia.name))
        self.assertTrue(self.perfil.disponible)
        imagen = self.client.get(reverse('repartidor_fotografia', args=[evento.pk]))
        self.assertEqual(imagen.status_code, 200)
        self.assertEqual(imagen['Content-Type'], 'image/jpeg')

        otro = User.objects.create_user(username='otro_foto')
        Repartidor.objects.create(user=otro, pin='1212')
        self.client.force_login(otro)
        self.assertEqual(
            self.client.get(reverse('repartidor_fotografia', args=[evento.pk])).status_code,
            404,
        )

    def test_foto_invalida_no_cambia_estado_ni_crea_historial(self):
        archivo = SimpleUploadedFile(
            'no-es-imagen.png', b'contenido invalido', content_type='image/png',
        )

        response = self.client.post(
            reverse('actualizar_estado', args=[self.pedido.pk]),
            {'estado': 'fallido', 'fotografia': archivo},
        )

        self.pedido.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.pedido.estado, 'en_viaje')
        self.assertFalse(HistorialEstado.objects.exists())

    def test_foto_mayor_a_limite_no_cambia_estado(self):
        archivo = SimpleUploadedFile(
            'grande.png', b'x' * (10 * 1024 * 1024 + 1), content_type='image/png',
        )

        self.client.post(
            reverse('actualizar_estado', args=[self.pedido.pk]),
            {'estado': 'entregado', 'fotografia': archivo},
        )

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'en_viaje')
        self.assertFalse(HistorialEstado.objects.exists())

    def test_fotografias_multiples_se_rechazan(self):
        self.client.post(
            reverse('actualizar_estado', args=[self.pedido.pk]),
            {'estado': 'entregado', 'fotografia': [self._imagen(), self._imagen()]},
        )

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'en_viaje')
        self.assertFalse(HistorialEstado.objects.exists())

    def test_foto_se_acepta_para_entrega_fallida(self):
        self.client.post(
            reverse('actualizar_estado', args=[self.pedido.pk]),
            {'estado': 'fallido', 'fotografia': self._imagen()},
        )

        self.pedido.refresh_from_db()
        evento = HistorialEstado.objects.get(pedido=self.pedido)
        self.assertEqual(self.pedido.estado, 'fallido')
        self.assertTrue(evento.fotografia.name.endswith('.jpg'))
        self.assertIn('Retornar el pedido al centro de distribución', evento.incidencia)

    def test_fallo_al_persistir_estado_revierte_historial_y_elimina_foto(self):
        with patch.object(Pedido, 'save', side_effect=IntegrityError('fallo simulado')):
            with self.assertRaises(IntegrityError):
                self.client.post(
                    reverse('actualizar_estado', args=[self.pedido.pk]),
                    {'estado': 'entregado', 'fotografia': self._imagen()},
                )

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'en_viaje')
        self.assertFalse(HistorialEstado.objects.exists())
        self.assertFalse(any(
            ruta.is_file() for ruta in Path(self.directorio_media).rglob('*')
        ))
