from datetime import timedelta
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
            is_operario=True,
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
            'datos_destinatario': 'Destinatario de prueba',
            'tamano_paquete': 'Tamaño indicado por comercio',
            'vehiculo_requerido': 'moto',
            'especificaciones_traslado': 'Manipular con cuidado',
            'fecha_hora_estimada_entrega': timezone.localtime(
                timezone.now() + timedelta(days=1)
            ).strftime('%Y-%m-%dT%H:%M'),
        }
        datos.update(cambios)
        return datos

    def test_usuario_anonimo_es_redirigido_al_login(self):
        self.client.logout()

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login/', respuesta.url)


    def test_usuario_autenticado_sin_is_operario_recibe_403(self):
        self.client.force_login(self.no_staff)

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 403)

        usuario_solo_staff = User.objects.create_user(
            username='staff_sin_rol_operario', is_staff=True,
        )
        self.client.force_login(usuario_solo_staff)
        self.assertEqual(self.client.get(self.url).status_code, 403)

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
        self.assertEqual(pedido.datos_destinatario, 'Destinatario de prueba')
        self.assertEqual(pedido.tamano_paquete, 'Tamaño indicado por comercio')
        self.assertEqual(
            pedido.vehiculo_requerido,
            'moto',
        )
        self.assertEqual(pedido.especificaciones_traslado, 'Manipular con cuidado')
        self.assertEqual(
            timezone.localtime(
                pedido.fecha_hora_estimada_entrega
            ).strftime('%Y-%m-%dT%H:%M'),
            datos['fecha_hora_estimada_entrega'],
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

        detalle = self.client.get(reverse(
            'operario:detalle_pedido', args=[pedido.pk]
        ))
        self.assertContains(detalle, 'Destinatario de prueba')
        self.assertContains(detalle, 'Tamaño indicado por comercio')
        self.assertContains(detalle, 'Moto')

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
            username='panel_operario', password='test1234', is_operario=True,
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

    def test_panel_y_detalle_muestran_pedido_comercio_e_historial(self):
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
        self.assertContains(detalle, 'Panel Comercio')
        self.assertContains(detalle, 'Calle 10')
        self.assertContains(detalle, '111')
        self.assertContains(detalle, 'Destinatario')
        self.assertContains(detalle, 'Tamaño del paquete')
        self.assertContains(detalle, 'Vehículo requerido')
        self.assertContains(detalle, 'No informado')
        self.assertContains(
            detalle,
            '<dd class="col-sm-8">Sin asignar</dd>',
            html=True,
        )
        self.assertContains(detalle, 'Historial del pedido')
        self.assertContains(detalle, 'Registrado')

    def test_historial_muestra_miniatura_ampliable(self):
        evento = HistorialEstado.objects.create(
            pedido=self.pedido,
            estado_nuevo='retirado',
            usuario=self.operario,
            fotografia='entregas/evidencia_prueba.jpg',
        )

        response = self.client.get(
            reverse('operario:detalle_pedido', args=[self.pedido.pk])
        )

        url_fotografia = reverse(
            'repartidor_fotografia',
            args=[evento.pk],
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="img-thumbnail"')
        self.assertContains(response, f'src="{url_fotografia}"')
        self.assertContains(response, f'href="{url_fotografia}"')
        self.assertContains(response, 'target="_blank"')

    def test_detalle_muestra_repartidor_asignado_y_no_indica_sin_asignar(self):
        repartidor = User.objects.create_user(
            username='repartidor_detalle', first_name='Rosa', last_name='Pérez',
        )
        self.pedido.repartidor = repartidor
        self.pedido.estado = 'asignado'
        self.pedido.save(update_fields=['repartidor', 'estado'])

        detalle = self.client.get(
            reverse('operario:detalle_pedido', args=[self.pedido.pk])
        )

        self.assertEqual(detalle.status_code, 200)
        self.assertContains(detalle, 'Rosa Pérez')
        self.assertNotContains(detalle, 'Sin asignar')

    def test_detalle_maneja_comercio_ausente_y_direccion_vacia(self):
        self.pedido.comercio = None
        self.pedido.save(update_fields=['comercio'])

        detalle_sin_comercio = self.client.get(
            reverse('operario:detalle_pedido', args=[self.pedido.pk])
        )

        self.assertContains(detalle_sin_comercio, 'Sin comercio')

        comercio_sin_direccion = Comercio.objects.create(
            nombre='Comercio sin dirección', direccion='', contacto='Contacto',
        )
        self.pedido.comercio = comercio_sin_direccion
        self.pedido.save(update_fields=['comercio'])

        detalle_sin_direccion = self.client.get(
            reverse('operario:detalle_pedido', args=[self.pedido.pk])
        )

        self.assertContains(detalle_sin_direccion, 'Sin dirección')

    def test_cancelacion_activa_solo_aparece_en_estados_permitidos(self):
        for estado in ('registrado', 'asignado'):
            with self.subTest(estado=estado):
                self.pedido.estado = estado
                self.pedido.save(update_fields=['estado'])

                detalle = self.client.get(
                    reverse('operario:detalle_pedido', args=[self.pedido.pk])
                )

                self.assertContains(detalle, 'Cancelar pedido')
                self.assertContains(detalle, 'method="post"')
                self.assertContains(detalle, 'onsubmit="return confirm(')

        for estado in ('retirado', 'en_viaje', 'entregado', 'fallido', 'cancelado'):
            with self.subTest(estado=estado):
                self.pedido.estado = estado
                self.pedido.save(update_fields=['estado'])

                detalle = self.client.get(
                    reverse('operario:detalle_pedido', args=[self.pedido.pk])
                )

                self.assertNotContains(detalle, 'cancelacion-pendiente')

    def test_usuario_sin_is_operario_no_accede_al_panel_ni_detalle(self):
        self.client.force_login(self.usuario_comun)

        self.assertEqual(self.client.get(reverse('operario:inicio')).status_code, 403)
        self.assertEqual(
            self.client.get(reverse('operario:detalle_pedido', args=[self.pedido.pk])).status_code,
            403,
        )

        usuario_solo_staff = User.objects.create_user(
            username='panel_staff_sin_rol', is_staff=True,
        )
        self.client.force_login(usuario_solo_staff)
        self.assertEqual(self.client.get(reverse('operario:inicio')).status_code, 403)

    def test_asignado_sin_aceptar_aparece_en_el_panel(self):
        repartidor_usuario = User.objects.create_user(
            username='panel_repartidor_pendiente', password='test1234',
        )
        Repartidor.objects.create(user=repartidor_usuario, pin='1111', disponible=True)
        self.pedido.repartidor = repartidor_usuario
        self.pedido.estado = 'asignado'
        self.pedido.fecha_hora_asignacion = timezone.now()
        self.pedido.fecha_hora_aceptacion = None
        self.pedido.save()

        lista = self.client.get(reverse('operario:inicio'))
        estado = self.client.get(reverse('operario:estado_pedidos'))

        self.assertContains(lista, 'PANEL-001')
        self.assertEqual(len(estado.json()['pedidos']), 1)
        self.assertEqual(estado.json()['pedidos'][0]['codigo'], 'PANEL-001')

    def test_buscar_pedido_por_codigo_redirige_al_detalle(self):
        response = self.client.get(
            reverse('operario:buscar_pedido'),
            {'q': 'PANEL-001'},
        )

        self.assertRedirects(
            response,
            reverse('operario:detalle_pedido', args=[self.pedido.pk]),
        )

    def test_buscar_pedido_por_id_redirige_al_detalle(self):
        response = self.client.get(
            reverse('operario:buscar_pedido'),
            {'q': str(self.pedido.pk)},
        )

        self.assertRedirects(
            response,
            reverse('operario:detalle_pedido', args=[self.pedido.pk]),
        )

    def test_buscar_pedido_inexistente_vuelve_al_panel(self):
        response = self.client.get(
            reverse('operario:buscar_pedido'),
            {'q': 'PEDIDO-QUE-NO-EXISTE'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('operario:inicio'))
        self.assertContains(
            response,
            'No se encontró ningún pedido con ese código o identificador.',
        )

    def test_usuario_sin_is_operario_no_puede_buscar_pedidos(self):
        self.client.force_login(self.usuario_comun)

        response = self.client.get(
            reverse('operario:buscar_pedido'),
            {'q': 'PANEL-001'},
        )

        self.assertEqual(response.status_code, 403)

    def test_historial_se_muestra_en_orden_cronologico_con_responsable(self):
        repartidor = User.objects.create_user(
            username='repartidor_historial',
            first_name='Juan',
            last_name='Perez',
            password='test1234',
        )

        evento_registrado = HistorialEstado.objects.create(
            pedido=self.pedido,
            estado_nuevo='registrado',
            usuario=self.operario,
        )

        evento_retirado = HistorialEstado.objects.create(
            pedido=self.pedido,
            estado_anterior='asignado',
            estado_nuevo='retirado',
            usuario=repartidor,
        )

        detalle = self.client.get(
            reverse('operario:detalle_pedido', args=[self.pedido.pk])
        )

        historial = list(detalle.context['historial'])

        self.assertEqual(detalle.status_code, 200)
        self.assertEqual(
            historial,
            [evento_registrado, evento_retirado],
        )
        self.assertContains(detalle, 'panel_operario')
        self.assertContains(detalle, 'Juan Perez')
        self.assertContains(
            detalle,
            timezone.localtime(evento_registrado.fecha).strftime('%d/%m/%Y %H:%M:%S'),
        )
        self.assertContains(
            detalle,
            timezone.localtime(evento_retirado.fecha).strftime('%d/%m/%Y %H:%M:%S'),
        )

    def test_asignado_y_aceptado_aparece_en_el_panel(self):
        repartidor_usuario = User.objects.create_user(
            username='panel_repartidor_aceptado', password='test1234',
        )
        Repartidor.objects.create(user=repartidor_usuario, pin='2222', disponible=True)
        self.pedido.repartidor = repartidor_usuario
        self.pedido.estado = 'asignado'
        self.pedido.fecha_hora_asignacion = None
        self.pedido.fecha_hora_aceptacion = timezone.now()
        self.pedido.save()

        lista = self.client.get(reverse('operario:inicio'))
        estado = self.client.get(reverse('operario:estado_pedidos'))

        self.assertContains(lista, 'PANEL-001')
        self.assertEqual(len(estado.json()['pedidos']), 1)
        self.assertEqual(estado.json()['pedidos'][0]['codigo'], 'PANEL-001')

    def test_panel_ordena_pedidos_por_antiguedad(self):
        anterior = Pedido.objects.create(
            codigo='PANEL-000', comercio=self.comercio,
            direccion_destino='Destino 0', estado='registrado',
        )
        Pedido.objects.filter(pk=anterior.pk).update(
            fecha_creacion=timezone.now() - timedelta(days=1),
        )

        lista = self.client.get(reverse('operario:inicio'))

        self.assertLess(
            lista.content.index(b'PANEL-000'),
            lista.content.index(b'PANEL-001'),
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
class CancelarPedidoTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_cancelacion', is_operario=True,
        )
        self.usuario_comun = User.objects.create_user(username='usuario_cancelacion')
        self.repartidor = User.objects.create_user(username='repartidor_cancelacion')
        self.perfil = Repartidor.objects.create(
            user=self.repartidor, pin='6712', disponible=False,
        )
        self.pedido = Pedido.objects.create(
            codigo='CANCELAR-001', estado='registrado',
        )
        self.url = reverse('operario:cancelar_pedido', args=[self.pedido.pk])
        self.client.force_login(self.operario)

    def test_cancela_pedido_registrado_y_registra_historial(self):
        response = self.client.post(self.url)

        self.pedido.refresh_from_db()
        evento = HistorialEstado.objects.get(pedido=self.pedido)
        self.assertRedirects(
            response, reverse('operario:detalle_pedido', args=[self.pedido.pk]),
        )
        self.assertEqual(self.pedido.estado, 'cancelado')
        self.assertEqual(evento.estado_anterior, 'registrado')
        self.assertEqual(evento.estado_nuevo, 'cancelado')
        self.assertEqual(evento.usuario, self.operario)
        self.assertIn('Cancelación solicitada por operario', evento.incidencia)

    def test_cancela_asignado_libera_repartidor_y_limpia_aceptacion(self):
        self.pedido.estado = 'asignado'
        self.pedido.repartidor = self.repartidor
        self.pedido.fecha_hora_asignacion = timezone.now()
        self.pedido.fecha_hora_aceptacion = timezone.now()
        self.pedido.save()

        response = self.client.post(self.url)

        self.pedido.refresh_from_db()
        self.perfil.refresh_from_db()
        evento = HistorialEstado.objects.get(pedido=self.pedido)
        self.client.force_login(self.repartidor)
        panel = self.client.get(reverse('repartidor'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse('operario:detalle_pedido', args=[self.pedido.pk]),
        )
        self.assertEqual(self.pedido.estado, 'cancelado')
        self.assertEqual(self.pedido.repartidor, self.repartidor)
        self.assertIsNone(self.pedido.fecha_hora_aceptacion)
        self.assertTrue(self.perfil.disponible)
        self.assertEqual(evento.estado_anterior, 'asignado')
        self.assertEqual(evento.estado_nuevo, 'cancelado')
        self.assertIn(self.repartidor.username, evento.incidencia)
        self.assertIsNone(panel.context['pedido_activo'])

    def test_rechaza_estados_que_no_se_pueden_cancelar(self):
        for estado in ('retirado', 'en_viaje', 'entregado', 'fallido', 'cancelado'):
            with self.subTest(estado=estado):
                self.pedido.estado = estado
                self.pedido.save(update_fields=['estado'])
                response = self.client.post(self.url)

                self.assertEqual(response.status_code, 400)
                self.pedido.refresh_from_db()
                self.assertEqual(self.pedido.estado, estado)
                self.assertFalse(
                    HistorialEstado.objects.filter(pedido=self.pedido).exists()
                )

    def test_boton_solo_se_muestra_para_registrado_o_asignado(self):
        for estado in ('registrado', 'asignado'):
            with self.subTest(estado=estado):
                self.pedido.estado = estado
                self.pedido.save(update_fields=['estado'])
                response = self.client.get(
                    reverse('operario:detalle_pedido', args=[self.pedido.pk])
                )
                self.assertContains(response, 'Cancelar pedido')
                self.assertContains(response, 'onsubmit="return confirm(')

        for estado in ('retirado', 'en_viaje', 'entregado', 'fallido', 'cancelado'):
            with self.subTest(estado=estado):
                self.pedido.estado = estado
                self.pedido.save(update_fields=['estado'])
                response = self.client.get(
                    reverse('operario:detalle_pedido', args=[self.pedido.pk])
                )
                self.assertNotContains(response, 'Cancelar pedido')

    def test_cancelacion_requiere_post_y_rol_operario(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

        self.client.force_login(self.usuario_comun)
        self.assertEqual(self.client.post(self.url).status_code, 403)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'registrado')

        self.client.logout()
        self.assertEqual(self.client.post(self.url).status_code, 302)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class CargarPedidoValidacionesTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_validaciones', password='test1234', is_operario=True,
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
            'datos_destinatario': 'Destinatario de prueba',
            'tamano_paquete': 'Tamaño indicado por comercio',
            'vehiculo_requerido': 'moto',
            'especificaciones_traslado': 'Manipular con cuidado',
            'fecha_hora_estimada_entrega': timezone.localtime(
                timezone.now() + timedelta(days=1)
            ).strftime('%Y-%m-%dT%H:%M'),
            **cambios,
        }

    def test_campos_obligatorios_y_fecha_invalida_no_crean_pedido(self):
        datos = self._datos_formulario(
            direccion_destino='',
            datos_destinatario='',
            tamano_paquete='',
            vehiculo_requerido='',
            especificaciones_traslado='',
            fecha_hora_estimada_entrega='fecha-invalida',
        )

        respuesta = self.client.post(self.url, datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].errors)
        self.assertTrue(respuesta.context['form'].has_error('datos_destinatario'))
        self.assertTrue(respuesta.context['form'].has_error('tamano_paquete'))
        self.assertTrue(respuesta.context['form'].has_error('vehiculo_requerido'))
        self.assertFalse(Pedido.objects.exists())

    def test_vehiculo_requerido_solo_acepta_opciones_validas(self):
        datos = self._datos_formulario(vehiculo_requerido='patineta')

        respuesta = self.client.post(self.url, datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].has_error('vehiculo_requerido'))
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
            'datos_destinatario': 'Destinatario de prueba',
            'tamano_paquete': 'Tamaño indicado por comercio',
            'vehiculo_requerido': 'moto',
            'especificaciones_traslado': 'Manipular con cuidado',
            'fecha_hora_estimada_entrega': timezone.localtime(
                timezone.now() + timedelta(days=1)
            ).strftime('%Y-%m-%dT%H:%M'),
        }
        formulario = PedidoForm(data=datos)
        self.assertTrue(formulario.is_valid(), formulario.errors)
        self.comercio.activo = False
        self.comercio.save(update_fields=['activo'])

        with self.assertRaises(ComercioInactivoError):
            _crear_pedido(formulario, self.operario)

        self.assertFalse(Pedido.objects.exists())


class RepartidoresOperarioTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_repartidores', password='test1234', is_operario=True,
        )
        self.usuario_comun = User.objects.create_user(
            username='usuario_repartidores', password='test1234',
        )
        self.client.force_login(self.operario)

    def test_lista_muestra_usuario_vehiculo_y_disponibilidad(self):
        usuario = User.objects.create_user(username='repartidor_lista')
        Repartidor.objects.create(
            user=usuario, pin='3124', disponible=True, vehiculo='bicicleta',
        )

        respuesta = self.client.get(reverse('operario:repartidores'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'repartidor_lista')
        self.assertContains(respuesta, 'Bicicleta')
        self.assertContains(respuesta, 'Disponible')
        self.assertContains(
            respuesta,
            'type="checkbox" role="switch" data-username="repartidor_lista"',
        )

    def test_alta_crea_usuario_y_perfil_de_forma_conjunta(self):
        respuesta = self.client.post(reverse('operario:nuevo_repartidor'), {
            'usuario': 'nuevo_repartidor',
            'nombre': 'Ana',
            'apellido': 'Pérez',
            'email': 'ana@example.test',
            'dni': '12345678',
            'vehiculo': 'bicicleta',
            'pin': '0123',
        })

        self.assertRedirects(respuesta, reverse('operario:repartidores'))
        usuario = User.objects.get(username='nuevo_repartidor')
        perfil = Repartidor.objects.get(user=usuario)
        self.assertEqual(usuario.first_name, 'Ana')
        self.assertEqual(usuario.last_name, 'Pérez')
        self.assertEqual(usuario.email, 'ana@example.test')
        self.assertFalse(usuario.has_usable_password())
        self.assertEqual(perfil.pin, '0123')
        self.assertEqual(perfil.vehiculo, 'bicicleta')
        self.assertFalse(perfil.disponible)

    def test_nombre_apellido_y_email_son_opcionales(self):
        respuesta = self.client.post(reverse('operario:nuevo_repartidor'), {
            'usuario': 'repartidor_sin_datos',
            'dni': '87654321',
            'vehiculo': 'moto',
            'pin': '0007',
        })

        self.assertRedirects(respuesta, reverse('operario:repartidores'))
        usuario = User.objects.get(username='repartidor_sin_datos')
        self.assertEqual((usuario.first_name, usuario.last_name, usuario.email), ('', '', ''))

    def test_pin_debe_tener_cuatro_digitos_y_ser_unico(self):
        respuesta = self.client.post(reverse('operario:nuevo_repartidor'), {
            'usuario': 'repartidor_pin_invalido',
            'vehiculo': 'moto',
            'pin': '12a4',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(User.objects.filter(username='repartidor_pin_invalido').exists())

        existente = User.objects.create_user(username='repartidor_pin_existente')
        Repartidor.objects.create(user=existente, pin='4567')
        respuesta = self.client.post(reverse('operario:nuevo_repartidor'), {
            'usuario': 'repartidor_pin_duplicado',
            'vehiculo': 'moto',
            'pin': '4567',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(User.objects.filter(username='repartidor_pin_duplicado').exists())

    def test_vehiculo_es_obligatorio_y_debe_pertenecer_a_las_opciones_del_modelo(self):
        url = reverse('operario:nuevo_repartidor')
        for datos in (
            {'usuario': 'sin_vehiculo', 'pin': '1001'},
            {'usuario': 'vehiculo_invalido', 'vehiculo': 'patineta', 'pin': '1002'},
        ):
            with self.subTest(datos=datos):
                respuesta = self.client.post(url, datos)
                self.assertEqual(respuesta.status_code, 200)
                self.assertTrue(respuesta.context['form'].has_error('vehiculo'))
                self.assertFalse(User.objects.filter(username=datos['usuario']).exists())

    def test_anonimo_y_usuario_sin_staff_no_acceden(self):
        self.client.logout()
        respuesta = self.client.get(reverse('operario:repartidores'))
        self.assertEqual(respuesta.status_code, 302)

        self.client.force_login(self.usuario_comun)
        for nombre in ('operario:repartidores', 'operario:nuevo_repartidor'):
            with self.subTest(nombre=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 403)


class EstadoRepartidoresTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_estado_lista', password='test1234', is_operario=True,
        )
        self.usuario_comun = User.objects.create_user(
            username='usuario_estado_lista', password='test1234',
        )
        self.usuario_repartidor = User.objects.create_user(username='repartidor_estado_lista')
        self.perfil = Repartidor.objects.create(
            user=self.usuario_repartidor, pin='4321', disponible=False,
        )
        self.url = reverse('operario:estado_repartidores')
        self.client.force_login(self.operario)

    def test_devuelve_disponibilidad_actual_de_cada_repartidor(self):
        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {'repartidores': [
                {'username': self.usuario_repartidor.username, 'disponible': False},
            ]},
        )

    def test_refleja_el_cambio_de_disponibilidad_hecho_por_el_repartidor(self):
        self.perfil.disponible = True
        self.perfil.save(update_fields=['disponible'])

        respuesta = self.client.get(self.url)

        self.assertEqual(
            respuesta.json()['repartidores'][0],
            {'username': self.usuario_repartidor.username, 'disponible': True},
        )

    def test_anonimo_y_usuario_sin_staff_no_acceden(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)

        self.client.force_login(self.usuario_comun)
        self.assertEqual(self.client.get(self.url).status_code, 403)


class CambiarEstadoRepartidorTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_estado_repartidor', password='test1234', is_operario=True,
        )
        self.usuario_comun = User.objects.create_user(
            username='usuario_estado_repartidor', password='test1234',
        )
        self.usuario_repartidor = User.objects.create_user(username='repartidor_estado')
        self.perfil = Repartidor.objects.create(
            user=self.usuario_repartidor, pin='9911', disponible=True,
        )
        self.url = reverse('operario:cambiar_estado_repartidor')
        self.client.force_login(self.operario)

    def test_deshabilita_repartidor_sin_pedidos_activos(self):
        respuesta = self.client.post(
            self.url, {'username': self.usuario_repartidor.username, 'activo': 'false'}
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            {'username': self.usuario_repartidor.username, 'activo': False},
        )
        self.usuario_repartidor.refresh_from_db()
        self.assertFalse(self.usuario_repartidor.is_active)

    def test_repartidor_deshabilitado_no_puede_iniciar_sesion_por_pin(self):
        self.client.post(
            self.url, {'username': self.usuario_repartidor.username, 'activo': 'false'}
        )
        self.client.logout()

        respuesta = self.client.post(reverse('repartidor_login_pin'), {'pin': '9911'})

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(
            self.client.session.get('_auth_user_id')
        )

    def test_rechaza_deshabilitar_con_pedido_en_curso(self):
        for indice, estado in enumerate(('asignado', 'retirado', 'en_viaje')):
            with self.subTest(estado=estado):
                Pedido.objects.create(
                    codigo=f'ESTADO-{indice}',
                    repartidor=self.usuario_repartidor,
                    estado=estado,
                )

                respuesta = self.client.post(
                    self.url,
                    {'username': self.usuario_repartidor.username, 'activo': 'false'},
                )

                self.assertEqual(respuesta.status_code, 400)
                self.assertEqual(
                    respuesta.json(), {'error': 'El repartidor tiene pedidos en curso'}
                )
                self.usuario_repartidor.refresh_from_db()
                self.assertTrue(self.usuario_repartidor.is_active)

    def test_reactivar_no_exige_ausencia_de_pedidos_en_curso(self):
        self.usuario_repartidor.is_active = False
        self.usuario_repartidor.save(update_fields=['is_active'])
        Pedido.objects.create(
            codigo='ESTADO-REACTIVAR',
            repartidor=self.usuario_repartidor,
            estado='en_viaje',
        )

        respuesta = self.client.post(
            self.url, {'username': self.usuario_repartidor.username, 'activo': 'true'}
        )

        self.assertEqual(respuesta.status_code, 200)
        self.usuario_repartidor.refresh_from_db()
        self.assertTrue(self.usuario_repartidor.is_active)

    def test_rechaza_datos_invalidos_o_repartidor_inexistente(self):
        for datos, estado in (
            ({'username': '', 'activo': 'true'}, 400),
            ({'username': 'no_existe', 'activo': 'true'}, 404),
            ({'username': self.usuario_repartidor.username, 'activo': '1'}, 400),
        ):
            with self.subTest(datos=datos):
                self.assertEqual(self.client.post(self.url, datos).status_code, estado)

    def test_requiere_metodo_post_y_rol_operario(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

        self.client.force_login(self.usuario_comun)
        self.assertEqual(
            self.client.post(
                self.url, {'username': self.usuario_repartidor.username, 'activo': 'false'}
            ).status_code,
            403,
        )

        self.client.logout()
        self.assertEqual(self.client.post(self.url, {}).status_code, 302)


class ComerciosOperarioTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_comercios', password='test1234', is_operario=True,
        )
        self.usuario_comun = User.objects.create_user(
            username='usuario_comercios', password='test1234',
        )
        self.client.force_login(self.operario)

    def test_lista_muestra_datos_y_estado_de_comercios(self):
        Comercio.objects.create(
            nombre='Comercio visible',
            direccion='Av. Central 123',
            contacto='contacto@example.test',
            activo=False,
        )

        respuesta = self.client.get(reverse('operario:comercios'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Comercio visible')
        self.assertContains(respuesta, 'Av. Central 123')
        self.assertContains(respuesta, 'contacto@example.test')
        self.assertContains(
            respuesta,
            'type="checkbox" role="switch" data-nombre="Comercio visible"',
        )

    def test_alta_persiste_comercio_activo_o_inactivo(self):
        for nombre, activo in (('Comercio activo nuevo', 'true'), ('Comercio inactivo nuevo', 'false')):
            with self.subTest(activo=activo):
                respuesta = self.client.post(reverse('operario:nuevo_comercio'), {
                    'nombre': nombre,
                    'direccion': 'Calle de prueba 456',
                    'contacto': '123456789',
                    'activo': activo,
                })

                self.assertRedirects(respuesta, reverse('operario:comercios'))
                comercio = Comercio.objects.get(nombre=nombre)
                self.assertEqual(comercio.direccion, 'Calle de prueba 456')
                self.assertEqual(comercio.contacto, '123456789')
                self.assertEqual(comercio.activo, activo == 'true')

    def test_cambiar_estado_comercio_por_nombre(self):
        comercio = Comercio.objects.create(
            nombre='Comercio estado', direccion='Calle 1', contacto='Contacto',
        )
        url = reverse('operario:cambiar_estado_comercio')

        respuesta = self.client.post(url, {'nombre': comercio.nombre, 'activo': 'false'})

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {'nombre': comercio.nombre, 'activo': False})
        comercio.refresh_from_db()
        self.assertFalse(comercio.activo)

    def test_cambiar_estado_rechaza_datos_invalidos_o_comercio_inexistente(self):
        url = reverse('operario:cambiar_estado_comercio')

        for datos, estado in (
            ({'nombre': '', 'activo': 'true'}, 400),
            ({'nombre': 'No existe', 'activo': 'true'}, 404),
            ({'nombre': 'No importa', 'activo': '1'}, 400),
        ):
            with self.subTest(datos=datos):
                self.assertEqual(self.client.post(url, datos).status_code, estado)

    def test_cambiar_estado_requiere_metodo_post_y_rol_operario(self):
        url = reverse('operario:cambiar_estado_comercio')
        self.assertEqual(self.client.get(url).status_code, 405)

        self.client.force_login(self.usuario_comun)
        self.assertEqual(
            self.client.post(url, {'nombre': 'Comercio', 'activo': 'true'}).status_code,
            403,
        )

        self.client.logout()
        self.assertEqual(self.client.post(url, {}).status_code, 302)

    def test_campos_y_estado_son_obligatorios_y_estado_debe_ser_valido(self):
        url = reverse('operario:nuevo_comercio')
        datos_incompletos = {
            'nombre': '', 'direccion': '', 'contacto': '', 'activo': '',
        }
        respuesta = self.client.post(url, datos_incompletos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].errors)
        self.assertFalse(Comercio.objects.exists())

        datos_invalidos = {
            'nombre': 'Comercio estado inválido',
            'direccion': 'Calle 1',
            'contacto': 'Contacto',
            'activo': 'desconocido',
        }
        respuesta = self.client.post(url, datos_invalidos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].has_error('activo'))
        self.assertFalse(Comercio.objects.exists())

    def test_nombre_duplicado_es_rechazado(self):
        Comercio.objects.create(nombre='Nombre ocupado', direccion='A', contacto='B')

        respuesta = self.client.post(reverse('operario:nuevo_comercio'), {
            'nombre': 'Nombre ocupado',
            'direccion': 'Calle nueva',
            'contacto': 'Contacto nuevo',
            'activo': 'true',
        })

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].errors)
        self.assertEqual(Comercio.objects.count(), 1)

    def test_anonimo_y_usuario_sin_staff_no_acceden(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('operario:comercios')).status_code, 302)

        self.client.force_login(self.usuario_comun)
        for nombre in ('operario:comercios', 'operario:nuevo_comercio'):
            with self.subTest(nombre=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 403)


class OperarioRoleAuthorizationTests(TestCase):
    def test_is_staff_solo_no_accede_a_ninguna_ruta_operativa(self):
        usuario = User.objects.create_user(username='solo_staff', is_staff=True)
        self.client.force_login(usuario)
        rutas_get = (
            ('operario:inicio', ()),
            ('operario:comercios', ()),
            ('operario:nuevo_comercio', ()),
            ('operario:repartidores', ()),
            ('operario:nuevo_repartidor', ()),
            ('operario:estado_repartidores', ()),
            ('operario:estado_pedidos', ()),
            ('operario:cargar_pedido', ()),
            ('operario:detalle_pedido', (1,)),
            ('operario:pedido_registrado', (1,)),
        )

        for nombre, args in rutas_get:
            with self.subTest(nombre=nombre):
                respuesta = self.client.get(reverse(nombre, args=args))
                self.assertEqual(respuesta.status_code, 403)

        respuesta = self.client.post(
            reverse('operario:asignar_repartidor', args=[1]),
            {},
        )
        self.assertEqual(respuesta.status_code, 403)

        respuesta = self.client.post(
            reverse('operario:reintentar_asignacion', args=[1]),
            {},
        )
        self.assertEqual(respuesta.status_code, 403)

    def test_is_operario_sin_is_staff_puede_entrar_al_modulo(self):
        usuario = User.objects.create_user(
            username='operario_sin_staff', is_operario=True,
        )
        self.client.force_login(usuario)

        respuesta = self.client.get(reverse('operario:inicio'))

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(usuario.is_staff)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class DespachoAutomaticoTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_despacho', password='test1234', is_operario=True,
        )
        self.comercio = Comercio.objects.create(
            nombre='Comercio despacho',
            direccion='Av. Siempre Viva 123',
            contacto='comercio@example.test',
        )
        self.url = reverse('operario:cargar_pedido')
        self.client.force_login(self.operario)

    def _datos(self, **cambios):
        respuesta = self.client.get(self.url)
        datos = {
            'clave_idempotencia': str(
                respuesta.context['form']['clave_idempotencia'].value()
            ),
            'comercio': str(self.comercio.pk),
            'direccion_destino': 'Calle Destino 456',
            'datos_destinatario': 'Destinatario de prueba',
            'tamano_paquete': 'Tamaño indicado por comercio',
            'vehiculo_requerido': 'moto',
            'especificaciones_traslado': 'Manipular con cuidado',
            'fecha_hora_estimada_entrega': timezone.localtime(
                timezone.now() + timedelta(days=1)
            ).strftime('%Y-%m-%dT%H:%M'),
            **cambios,
        }
        return datos

    def test_asignacion_automatica_al_crear_pedido_con_candidato(self):
        repartidor = User.objects.create_user(username='repartidor_moto_despacho')
        perfil = Repartidor.objects.create(
            user=repartidor, pin='1111', disponible=True, vehiculo='moto',
        )

        respuesta = self.client.post(self.url, self._datos())

        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.estado, 'asignado')
        self.assertEqual(pedido.repartidor, repartidor)
        self.assertIsNotNone(pedido.fecha_hora_asignacion)
        self.assertIsNone(pedido.fecha_hora_aceptacion)
        evento = HistorialEstado.objects.get(
            pedido=pedido, estado_nuevo='asignado',
        )
        self.assertEqual(evento.estado_anterior, 'registrado')
        self.assertIn('Asignación automática', evento.incidencia)
        self.assertIn(repartidor.username, evento.incidencia)

    def test_asignacion_manual_al_crear_pedido_con_vehiculo_correcto(self):
        repartidor = User.objects.create_user(username='repartidor_manual_despacho')
        perfil = Repartidor.objects.create(
            user=repartidor, pin='2222', disponible=True, vehiculo='moto',
        )

        respuesta = self.client.post(self.url, self._datos(
            repartidor=str(perfil.pk),
        ))

        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.estado, 'asignado')
        self.assertEqual(pedido.repartidor, repartidor)
        self.assertIn('Asignado por operario', HistorialEstado.objects.get(
            pedido=pedido, estado_nuevo='asignado',
        ).incidencia)

    def test_asignacion_manual_con_vehiculo_distinto_se_rechaza(self):
        repartidor = User.objects.create_user(username='repartidor_auto_despacho')
        perfil = Repartidor.objects.create(
            user=repartidor, pin='3333', disponible=True, vehiculo='auto',
        )

        respuesta = self.client.post(self.url, self._datos(
            repartidor=str(perfil.pk),
        ))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context['form'].has_error('repartidor'))
        self.assertFalse(Pedido.objects.exists())

    def test_no_se_asigna_sin_candidato_del_vehiculo_requerido(self):
        Repartidor.objects.create(
            user=User.objects.create_user(username='repartidor_auto'),
            pin='4444', disponible=True, vehiculo='auto',
        )

        respuesta = self.client.post(self.url, self._datos(
            vehiculo_requerido='camion',
        ))

        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.estado, 'registrado')
        self.assertIsNone(pedido.repartidor)
        self.assertFalse(HistorialEstado.objects.filter(
            pedido=pedido, estado_nuevo='asignado',
        ).exists())

    def test_no_se_asigna_candidato_ocupado_ni_inactivo(self):
        ocupado = User.objects.create_user(username='repartidor_ocupado')
        Repartidor.objects.create(
            user=ocupado, pin='5555', disponible=True, vehiculo='moto',
        )
        Pedido.objects.create(
            codigo='OCUPADO-001', repartidor=ocupado, estado='asignado',
        )
        inactivo = User.objects.create_user(
            username='repartidor_inactivo_despacho', is_active=False,
        )
        Repartidor.objects.create(
            user=inactivo, pin='6666', disponible=True, vehiculo='moto',
        )

        respuesta = self.client.post(self.url, self._datos())

        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.exclude(codigo='OCUPADO-001').get()
        self.assertEqual(pedido.estado, 'registrado')
        self.assertIsNone(pedido.repartidor)

    def test_se_prefiere_repartidor_con_disponible_desde_mas_antiguo(self):
        primero = User.objects.create_user(username='repartidor_cola_primero')
        perfil_primero = Repartidor.objects.create(
            user=primero, pin='7777', disponible=True, vehiculo='moto',
        )
        segundo = User.objects.create_user(username='repartidor_cola_segundo')
        perfil_segundo = Repartidor.objects.create(
            user=segundo, pin='8888', disponible=True, vehiculo='moto',
        )
        ahora = timezone.now()
        Repartidor.objects.filter(pk=perfil_primero.pk).update(
            disponible_desde=ahora - timedelta(hours=2),
        )
        Repartidor.objects.filter(pk=perfil_segundo.pk).update(
            disponible_desde=ahora - timedelta(hours=1),
        )

        respuesta = self.client.post(self.url, self._datos())

        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get(estado='asignado')
        self.assertEqual(pedido.repartidor, primero)

    def test_el_historial_de_viajes_no_altera_el_orden_fifo(self):
        con_viaje = User.objects.create_user(username='repartidor_con_viaje')
        perfil_con_viaje = Repartidor.objects.create(
            user=con_viaje, pin='9999', disponible=True, vehiculo='moto',
        )
        Pedido.objects.create(
            codigo='VIAJE-RECIENTE', repartidor=con_viaje, estado='entregado',
            fecha_hora_asignacion=timezone.now() - timedelta(days=1),
        )
        sin_viaje = User.objects.create_user(username='repartidor_sin_viaje')
        perfil_sin_viaje = Repartidor.objects.create(
            user=sin_viaje, pin='1000', disponible=True, vehiculo='moto',
        )
        ahora = timezone.now()
        Repartidor.objects.filter(pk=perfil_con_viaje.pk).update(
            disponible_desde=ahora - timedelta(hours=2),
        )
        Repartidor.objects.filter(pk=perfil_sin_viaje.pk).update(
            disponible_desde=ahora - timedelta(hours=1),
        )

        respuesta = self.client.post(self.url, self._datos())

        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get(estado='asignado')
        self.assertEqual(pedido.repartidor, con_viaje)


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class AlertaSinRepartidorTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_alerta', password='test1234', is_operario=True,
        )
        self.usuario_comun = User.objects.create_user(
            username='usuario_alerta', password='test1234',
        )
        self.comercio = Comercio.objects.create(
            nombre='Comercio alerta', direccion='Calle 1', contacto='111',
        )
        self.afectado = Pedido.objects.create(
            codigo='ALERTA-001', comercio=self.comercio, estado='registrado',
            vehiculo_requerido='moto',
        )
        self.asignado = Pedido.objects.create(
            codigo='ALERTA-002', comercio=self.comercio, estado='asignado',
        )
        self.client.force_login(self.operario)

    def test_panel_y_detalle_muestran_alerta_y_boton(self):
        lista = self.client.get(reverse('operario:inicio'))
        detalle = self.client.get(
            reverse('operario:detalle_pedido', args=[self.afectado.pk])
        )

        for respuesta in (lista, detalle):
            self.assertEqual(respuesta.status_code, 200)
            self.assertContains(respuesta, 'Pedido sin repartidor disponible')
            self.assertContains(respuesta, 'Reintentar asignación')
            self.assertContains(
                respuesta,
                reverse('operario:reintentar_asignacion', args=[self.afectado.pk]),
            )

    def test_notificacion_flotizante_marca_los_pedidos_afectados(self):
        for respuesta in (
            self.client.get(reverse('operario:inicio')),
            self.client.get(
                reverse('operario:detalle_pedido', args=[self.afectado.pk])
            ),
        ):
            self.assertContains(respuesta, 'id="alerta-sin-repartidor"')
            self.assertContains(respuesta, 'position-fixed top-0 end-0')
            self.assertEqual(
                [
                    pedido.codigo
                    for pedido in respuesta.context['pedidos_sin_repartidor']
                ],
                ['ALERTA-001'],
            )

    def test_estado_pedidos_incluye_alerta_y_url_de_reintento(self):
        respuesta = self.client.get(reverse('operario:estado_pedidos'))

        self.assertEqual(respuesta.status_code, 200)
        por_codigo = {
            pedido['codigo']: pedido for pedido in respuesta.json()['pedidos']
        }
        self.assertTrue(por_codigo['ALERTA-001']['sin_repartidor'])
        self.assertFalse(por_codigo['ALERTA-002']['sin_repartidor'])
        self.assertEqual(
            por_codigo['ALERTA-001']['url_reintentar'],
            reverse('operario:reintentar_asignacion', args=[self.afectado.pk]),
        )

    def test_reintentar_sin_candidatos_conserva_alerta(self):
        respuesta = self.client.post(
            reverse('operario:reintentar_asignacion', args=[self.afectado.pk]),
            {},
            follow=True,
        )

        self.afectado.refresh_from_db()
        self.assertEqual(self.afectado.estado, 'registrado')
        self.assertIsNone(self.afectado.repartidor)
        self.assertContains(respuesta, 'Pedido sin repartidor disponible')
        self.assertFalse(HistorialEstado.objects.filter(
            pedido=self.afectado, estado_nuevo='asignado',
        ).exists())

    def test_reintentar_asigna_cuando_aparece_candidato_compatible(self):
        reintentar = reverse('operario:reintentar_asignacion', args=[self.afectado.pk])

        self.client.post(reintentar, {})
        self.afectado.refresh_from_db()
        self.assertEqual(self.afectado.estado, 'registrado')

        repartidor = User.objects.create_user(username='repartidor_reintento')
        Repartidor.objects.create(
            user=repartidor, pin='1234', disponible=True, vehiculo='moto',
        )

        respuesta = self.client.post(reintentar, {}, follow=True)

        self.afectado.refresh_from_db()
        self.assertEqual(self.afectado.estado, 'asignado')
        self.assertEqual(self.afectado.repartidor, repartidor)
        self.assertIsNotNone(self.afectado.fecha_hora_asignacion)
        self.assertContains(respuesta, 'Pedido asignado')
        self.assertIn('Asignación automática', HistorialEstado.objects.get(
            pedido=self.afectado, estado_nuevo='asignado',
        ).incidencia)

        estado = self.client.get(reverse('operario:estado_pedidos')).json()
        alerta_activa = any(
            pedido['codigo'] == 'ALERTA-001' and pedido['sin_repartidor']
            for pedido in estado['pedidos']
        )
        self.assertFalse(alerta_activa)

    def test_reintentar_requiere_post_y_rol_operario(self):
        url = reverse('operario:reintentar_asignacion', args=[self.afectado.pk])

        self.assertEqual(self.client.get(url).status_code, 405)

        self.client.force_login(self.usuario_comun)
        self.assertEqual(self.client.post(url, {}).status_code, 403)

    def test_alerta_aparece_tras_rechazo_del_repartidor(self):
        repartidor = User.objects.create_user(
            username='repartidor_rechaza', password='test1234',
        )
        perfil = Repartidor.objects.create(
            user=repartidor, pin='4321', disponible=True, vehiculo='moto',
        )

        self.client.post(
            reverse('operario:asignar_repartidor', args=[self.afectado.pk]),
            {'repartidor': perfil.pk},
        )
        self.client.force_login(repartidor)
        self.client.post(reverse('repartidor_rechazar', args=[self.afectado.pk]))

        self.afectado.refresh_from_db()
        self.assertEqual(self.afectado.estado, 'registrado')
        self.assertIsNone(self.afectado.repartidor)
        self.client.force_login(self.operario)
        lista = self.client.get(reverse('operario:inicio'))
        self.assertContains(lista, 'Pedido sin repartidor disponible')

    def test_alerta_aparece_tras_expiracion_de_espera(self):
        repartidor = User.objects.create_user(
            username='repartidor_expirado', password='test1234',
        )
        perfil = Repartidor.objects.create(
            user=repartidor, pin='5678', disponible=True, vehiculo='moto',
        )

        self.client.post(
            reverse('operario:asignar_repartidor', args=[self.afectado.pk]),
            {'repartidor': perfil.pk},
        )
        self.afectado.fecha_hora_asignacion = timezone.now() - timedelta(seconds=301)
        self.afectado.save(update_fields=['fecha_hora_asignacion'])

        self.client.force_login(repartidor)
        self.client.get(reverse('repartidor'))

        self.afectado.refresh_from_db()
        self.assertEqual(self.afectado.estado, 'registrado')
        self.assertIsNone(self.afectado.repartidor)
        self.client.force_login(self.operario)
        lista = self.client.get(reverse('operario:inicio'))
        self.assertContains(lista, 'Pedido sin repartidor disponible')


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class CascadaReasignacionTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_cascada', password='test1234', is_operario=True,
        )
        self.comercio = Comercio.objects.create(
            nombre='Comercio cascada', direccion='Calle 30', contacto='333',
        )
        self.pedido = Pedido.objects.create(
            codigo='CASC-001', comercio=self.comercio,
            estado='registrado', vehiculo_requerido='moto',
        )
        self.r1 = User.objects.create_user(
            username='cascada_r1', password='test1234',
            first_name='R', last_name='Uno',
        )
        self.perfil_r1 = Repartidor.objects.create(
            user=self.r1, pin='1111', disponible=True, vehiculo='moto',
        )
        self.r2 = User.objects.create_user(
            username='cascada_r2', password='test1234',
            first_name='R', last_name='Dos',
        )
        self.perfil_r2 = Repartidor.objects.create(
            user=self.r2, pin='2222', disponible=True, vehiculo='moto',
        )
        self.client.force_login(self.operario)

    def _asignar_a_r1(self):
        self.client.post(
            reverse('operario:asignar_repartidor', args=[self.pedido.pk]),
            {'repartidor': self.perfil_r1.pk},
        )

    def _rechazar(self, pedido):
        pedido.refresh_from_db()
        self.client.force_login(pedido.repartidor)
        self.client.post(reverse('repartidor_rechazar', args=[pedido.pk]))
        self.client.force_login(self.operario)

    def _sin_alerta(self):
        inicio = self.client.get(reverse('operario:inicio'))
        self.assertEqual(list(inicio.context['pedidos_sin_repartidor']), [])
        estado = self.client.get(reverse('operario:estado_pedidos')).json()
        self.assertFalse(any(
            pedido['sin_repartidor'] for pedido in estado['pedidos']
        ))

    def test_rechazo_reasigna_al_siguiente_candidato_sin_alerta(self):
        self._asignar_a_r1()
        self._rechazar(self.pedido)

        self.pedido.refresh_from_db()
        self.perfil_r1.refresh_from_db()
        self.perfil_r2.refresh_from_db()

        self.assertEqual(self.pedido.estado, 'asignado')
        self.assertEqual(self.pedido.repartidor, self.r2)
        self.assertFalse(self.perfil_r1.disponible)
        self.assertTrue(self.perfil_r2.disponible)

        eventos = list(self.pedido.historial.order_by('pk'))
        self.assertEqual(
            [evento.estado_nuevo for evento in eventos],
            ['asignado', 'registrado', 'asignado'],
        )
        self.assertEqual(
            eventos[1].incidencia, 'Rechazado por repartidor R Uno',
        )
        self.assertIn('Asignación automática', eventos[2].incidencia)
        self.assertIn(self.r2.get_full_name(), eventos[2].incidencia)
        self._sin_alerta()

    def test_expiracion_reasigna_al_siguiente_candidato_sin_alerta(self):
        self._asignar_a_r1()
        Pedido.objects.filter(pk=self.pedido.pk).update(
            fecha_hora_asignacion=timezone.now() - timedelta(seconds=301),
        )

        self.client.get(reverse('operario:inicio'))

        self.pedido.refresh_from_db()
        self.perfil_r1.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'asignado')
        self.assertEqual(self.pedido.repartidor, self.r2)
        self.assertFalse(self.perfil_r1.disponible)

        eventos = list(self.pedido.historial.order_by('pk'))
        self.assertIn('expiración', eventos[1].incidencia)
        self.assertIn('Asignación automática', eventos[2].incidencia)
        self._sin_alerta()

    def test_segundo_rechazo_deja_pedido_registrado_y_muestra_alerta(self):
        self._asignar_a_r1()
        self._rechazar(self.pedido)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.repartidor, self.r2)

        self._rechazar(self.pedido)
        self.pedido.refresh_from_db()

        self.assertEqual(self.pedido.estado, 'registrado')
        self.assertIsNone(self.pedido.repartidor)

        inicio = self.client.get(reverse('operario:inicio'))
        self.assertContains(inicio, 'Pedido sin repartidor disponible')
        self.assertEqual(
            [pedido.codigo for pedido in inicio.context['pedidos_sin_repartidor']],
            ['CASC-001'],
        )

        estado = self.client.get(reverse('operario:estado_pedidos')).json()
        afectado = next(
            pedido for pedido in estado['pedidos'] if pedido['codigo'] == 'CASC-001'
        )
        self.assertTrue(afectado['sin_repartidor'])


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class ColaFifoReasignacionTests(TestCase):
    def setUp(self):
        self.operario = User.objects.create_user(
            username='operario_fifo', password='test1234', is_operario=True,
        )
        self.comercio = Comercio.objects.create(
            nombre='Comercio fifo', direccion='Calle 40', contacto='444',
        )
        self.pedido = Pedido.objects.create(
            codigo='FIFO-001', comercio=self.comercio,
            estado='registrado', vehiculo_requerido='moto',
        )
        self.perfiles = {}
        for indice, username in enumerate(
            ('fifo_r1', 'fifo_r2', 'fifo_r3'), start=1,
        ):
            usuario = User.objects.create_user(
                username=username, password='test1234',
                first_name=username, last_name='Cola',
            )
            self.perfiles[username] = Repartidor.objects.create(
                user=usuario, pin=f'210{indice}',
                disponible=True, vehiculo='moto',
            )
        ahora = timezone.now()
        for horas, username in zip(
            (3, 2, 1), ('fifo_r1', 'fifo_r2', 'fifo_r3'),
        ):
            Repartidor.objects.filter(
                pk=self.perfiles[username].pk,
            ).update(disponible_desde=ahora - timedelta(hours=horas))
        self.client.force_login(self.operario)

    def _rechazar(self, perfil):
        self.client.force_login(perfil.user)
        self.client.post(
            reverse('repartidor_rechazar', args=[self.pedido.pk]),
        )
        self.client.force_login(self.operario)

    def _repartidor_actual(self):
        self.pedido.refresh_from_db()
        return self.pedido.repartidor

    def test_cola_fifo_tras_rechazos_y_reactivacion(self):
        self.client.post(
            reverse('operario:asignar_repartidor', args=[self.pedido.pk]),
            {},
        )
        self.assertEqual(
            self._repartidor_actual(), self.perfiles['fifo_r1'].user,
        )

        self._rechazar(self.perfiles['fifo_r1'])
        self.assertEqual(
            self._repartidor_actual(), self.perfiles['fifo_r2'].user,
        )

        self.client.force_login(self.perfiles['fifo_r1'].user)
        self.client.post(reverse('repartidor_toggle_disponibilidad'))
        self.client.force_login(self.operario)
        self.perfiles['fifo_r1'].refresh_from_db()
        self.perfiles['fifo_r3'].refresh_from_db()
        self.assertTrue(self.perfiles['fifo_r1'].disponible)
        self.assertGreater(
            self.perfiles['fifo_r1'].disponible_desde,
            self.perfiles['fifo_r3'].disponible_desde,
        )

        self._rechazar(self.perfiles['fifo_r2'])
        self.assertEqual(
            self._repartidor_actual(), self.perfiles['fifo_r3'].user,
        )

        self._rechazar(self.perfiles['fifo_r3'])
        self.assertEqual(
            self._repartidor_actual(), self.perfiles['fifo_r1'].user,
        )
