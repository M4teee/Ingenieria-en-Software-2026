from django.test import TestCase, override_settings
from django.urls import reverse

from main.repartidor.models import Repartidor
from main.users.models import User


@override_settings(ALLOWED_HOSTS=['testserver'])
class PortadaYAccesosTests(TestCase):
    def test_portada_publica_es_seguimiento_y_muestra_accesos_por_rol(self):
        response = self.client.get(reverse('root'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clienteFinal/index.html')
        self.assertContains(response, 'Tu envío, en cada etapa.')
        self.assertContains(response, 'name="codigo"')
        self.assertContains(response, 'Iniciar sesión como operario')
        self.assertContains(response, 'Iniciar sesión como repartidor')
        self.assertContains(response, f"{reverse('login')}?next={reverse('operario:inicio')}")
        self.assertContains(response, reverse('repartidor_login_pin'))
        self.assertNotContains(response, 'Panel operario')
        self.assertNotContains(response, 'Administración')

    def test_busqueda_desde_la_raiz_conserva_el_flujo_publico(self):
        from main.repartidor.models import Pedido

        pedido = Pedido.objects.create(codigo='ROOT-CODE-123', estado='registrado')

        response = self.client.get(reverse('root'), {'codigo': pedido.codigo})

        self.assertRedirects(
            response,
            reverse('seguimiento', args=[pedido.codigo]),
        )

    def test_operario_va_al_panel_y_no_al_admin(self):
        user = User.objects.create_user(username='operario_home', is_staff=True)
        self.client.force_login(user)

        response = self.client.get(reverse('root'))

        self.assertRedirects(response, reverse('operario:inicio'))

    def test_login_operario_llega_al_panel_operativo(self):
        User.objects.create_user(
            username='operario_login',
            password='clave-prueba',
            is_staff=True,
        )

        response = self.client.post(reverse('login'), {
            'username': 'operario_login',
            'password': 'clave-prueba',
            'next': reverse('operario:inicio'),
        })

        self.assertRedirects(response, reverse('operario:inicio'))

    def test_repartidor_va_a_su_panel(self):
        user = User.objects.create_user(username='repartidor_home')
        Repartidor.objects.create(user=user, pin='6543')
        self.client.force_login(user)

        response = self.client.get(reverse('root'))

        self.assertRedirects(response, reverse('repartidor'))

    def test_panel_operario_muestra_una_accion_de_carga_y_no_seguimiento(self):
        user = User.objects.create_user(username='operario_panel', is_staff=True)
        self.client.force_login(user)

        response = self.client.get(reverse('operario:inicio'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.count(b'Cargar pedido'), 1)
        self.assertContains(response, reverse('admin:index'))
        self.assertNotContains(response, reverse('clienteFinal'))
        self.assertNotContains(response, 'Seguimiento</a>')

    def test_panel_repartidor_no_muestra_accesos_de_cliente_u_operario(self):
        user = User.objects.create_user(username='repartidor_panel')
        Repartidor.objects.create(user=user, pin='6542')
        self.client.force_login(user)

        response = self.client.get(reverse('repartidor'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tu pedido actual')
        self.assertContains(response, 'Historial de tus pedidos')
        self.assertNotContains(response, reverse('clienteFinal'))
        self.assertNotContains(response, reverse('operario:inicio'))
        self.assertNotContains(response, reverse('admin:index'))

    def test_django_admin_conserva_el_permiso_staff_y_rechaza_usuarios_comunes(self):
        operario = User.objects.create_user(username='operario_admin', is_staff=True)
        usuario = User.objects.create_user(username='usuario_admin')

        self.client.force_login(operario)
        self.assertEqual(self.client.get(reverse('admin:index')).status_code, 200)
        self.assertFalse(operario.is_superuser)

        self.client.force_login(usuario)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
