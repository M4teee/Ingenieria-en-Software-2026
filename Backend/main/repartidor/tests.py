from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.operario.models import Comercio
from main.repartidor.models import HistorialPedido, Pedido, RepartidorPerfil
from main.users.models import User


class TestBaseHU18(TestCase):
    def setUp(self):
        self.comercio = Comercio.objects.create(
            nombre='Panadería Sol',
            direccion='Calle Falsa 123',
            contacto='123456789',
        )
        self.repartidor = User.objects.create_user(
            username='juan', password='pass', first_name='Juan', last_name='Pérez')
        self.perfil = RepartidorPerfil.objects.create(user=self.repartidor, disponible=True)
        self.client.force_login(self.repartidor)

    def asignar_pedido(self, segundos_transcurridos=0):
        return Pedido.objects.create(
            comercio=self.comercio,
            estado='asignado',
            repartidor=self.repartidor,
            fecha_hora_asignacion=timezone.now() - timedelta(seconds=segundos_transcurridos),
        )


class Escenario1AceptarEnTiempoTests(TestBaseHU18):
    def test_aceptar_dentro_de_5_minutos_confirma_el_retiro(self):
        pedido = self.asignar_pedido(segundos_transcurridos=60)
        r = self.client.post(reverse('repartidor_aceptar', args=[pedido.id]))
        self.assertRedirects(r, reverse('repartidor'))
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'retirado')
        self.assertEqual(pedido.repartidor, self.repartidor)

    def test_aceptar_detiene_el_temporizador(self):
        pedido = self.asignar_pedido(segundos_transcurridos=60)
        self.client.post(reverse('repartidor_aceptar', args=[pedido.id]))
        pedido.refresh_from_db()
        self.assertIsNone(pedido.fecha_hora_asignacion)

    def test_aceptar_registra_evento_en_historial(self):
        pedido = self.asignar_pedido()
        self.client.post(reverse('repartidor_aceptar', args=[pedido.id]))
        self.assertTrue(
            HistorialPedido.objects.filter(
                pedido=pedido, descripcion='Aceptado por repartidor Juan Pérez').exists())

    def test_aceptar_no_cambia_disponibilidad(self):
        pedido = self.asignar_pedido()
        self.client.post(reverse('repartidor_aceptar', args=[pedido.id]))
        self.perfil.refresh_from_db()
        self.assertTrue(self.perfil.disponible)

    def test_muestra_cuenta_regresiva_restante(self):
        inicio = timezone.now()
        with patch('main.repartidor.views.timezone.now', return_value=inicio):
            self.asignar_pedido(segundos_transcurridos=100)
            r = self.client.get(reverse('repartidor'))
        self.assertContains(r, 'Aceptar viaje')
        self.assertContains(r, 'Rechazar viaje')
        self.assertEqual(r.context['segundos_restantes'], 200)


class Escenario2RechazoExplicitoTests(TestBaseHU18):
    def test_rechazar_libera_el_pedido_a_registrado(self):
        pedido = self.asignar_pedido()
        r = self.client.post(reverse('repartidor_rechazar', args=[pedido.id]))
        self.assertRedirects(r, reverse('repartidor'))
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'registrado')
        self.assertIsNone(pedido.repartidor)

    def test_rechazar_registra_evento_con_nombre(self):
        pedido = self.asignar_pedido()
        self.client.post(reverse('repartidor_rechazar', args=[pedido.id]))
        self.assertTrue(
            HistorialPedido.objects.filter(
                pedido=pedido,
                descripcion='Rechazado por repartidor Juan Pérez').exists())

    def test_rechazar_marca_repartidor_no_disponible(self):
        self.asignar_pedido()
        self.client.post(reverse('repartidor_rechazar', args=[self.repartidor.pedidos.first().id]))
        self.perfil.refresh_from_db()
        self.assertFalse(self.perfil.disponible)


class Escenario3ExpiracionTests(TestBaseHU18):
    def test_expiracion_en_home_libera_pedido_y_marca_no_disponible(self):
        pedido = self.asignar_pedido(segundos_transcurridos=301)
        r = self.client.get(reverse('repartidor'))
        self.assertContains(r, 'No disponible')
        self.assertContains(r, 'tiempo de espera se agotó')
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'registrado')
        self.assertIsNone(pedido.repartidor)
        self.perfil.refresh_from_db()
        self.assertFalse(self.perfil.disponible)

    def test_expiracion_registra_desasignacion_en_historial(self):
        pedido = self.asignar_pedido(segundos_transcurridos=300)
        self.client.get(reverse('repartidor'))
        self.assertTrue(
            HistorialPedido.objects.filter(
                pedido=pedido,
                descripcion__contains='expiración del tiempo de espera').exists())

    def test_aceptar_tras_expiracion_libera_el_pedido(self):
        pedido = self.asignar_pedido(segundos_transcurridos=310)
        self.client.post(reverse('repartidor_aceptar', args=[pedido.id]))
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'registrado')
        self.assertIsNone(pedido.repartidor)
        self.perfil.refresh_from_db()
        self.assertFalse(self.perfil.disponible)

    def test_expiracion_al_limite_exacto_de_300_segundos(self):
        # Al cumplir 300 segundos el tiempo está agotado (Escenario 3).
        pedido = self.asignar_pedido(segundos_transcurridos=300)
        self.client.post(reverse('repartidor_aceptar', args=[pedido.id]))
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'registrado')

    def test_aceptar_justo_antes_del_limite(self):
        pedido = self.asignar_pedido(segundos_transcurridos=299)
        self.client.post(reverse('repartidor_aceptar', args=[pedido.id]))
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'retirado')


class SeguridadTests(TestBaseHU18):
    def test_otro_repartidor_no_puede_aceptar(self):
        pedido = self.asignar_pedido()
        otro = User.objects.create_user(username='otro', password='pass')
        self.client.force_login(otro)
        r = self.client.post(reverse('repartidor_aceptar', args=[pedido.id]))
        self.assertEqual(r.status_code, 400)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'asignado')

    def test_aceptar_requiere_post(self):
        pedido = self.asignar_pedido()
        r = self.client.get(reverse('repartidor_aceptar', args=[pedido.id]))
        self.assertEqual(r.status_code, 405)

    def test_vista_requiere_login(self):
        self.client.logout()
        r = self.client.get(reverse('repartidor'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('login', r.url)

    def test_superusuario_es_redirigido_al_admin(self):
        admin = User.objects.create_superuser(username='root', password='pass')
        self.client.force_login(admin)
        r = self.client.get(reverse('repartidor'))
        self.assertRedirects(r, '/admin/')
