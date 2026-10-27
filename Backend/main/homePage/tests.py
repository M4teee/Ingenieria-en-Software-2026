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
        user = User.objects.create_user(username='operario_home', is_operario=True)
        self.client.force_login(user)

        response = self.client.get(reverse('root'))

        self.assertRedirects(response, reverse('operario:inicio'))

    def test_login_operario_llega_al_panel_operativo(self):
        User.objects.create_user(
            username='operario_login',
            password='clave-prueba',
            is_operario=True,
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

    def test_panel_operario_muestra_una_accion_sin_acceso_a_admin_ni_seguimiento(self):
        user = User.objects.create_user(username='operario_panel', is_operario=True)
        self.client.force_login(user)

        response = self.client.get(reverse('operario:inicio'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.count(b'Cargar pedido'), 1)
        self.assertNotContains(response, reverse('admin:index'))
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

    def test_django_admin_conserva_is_staff_independiente_de_is_operario(self):
        usuario_admin = User.objects.create_user(username='admin_sin_rol_operario', is_staff=True)
        usuario = User.objects.create_user(username='usuario_admin')

        self.client.force_login(usuario_admin)
        respuesta_admin = self.client.get(reverse('admin:index'))
        self.assertEqual(respuesta_admin.status_code, 200)
        self.assertNotContains(
            respuesta_admin,
            f'class="nav-link" href="{reverse("operario:inicio")}"',
        )
        self.assertEqual(self.client.get(reverse('operario:inicio')).status_code, 403)
        self.assertFalse(usuario_admin.is_superuser)

        usuario_operario_admin = User.objects.create_user(
            username='admin_y_operario', is_staff=True, is_operario=True,
        )
        self.client.force_login(usuario_operario_admin)
        respuesta_admin = self.client.get(reverse('admin:index'))
        self.assertContains(
            respuesta_admin,
            f'class="nav-link" href="{reverse("operario:inicio")}"',
        )

        self.client.force_login(usuario)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_is_operario_no_otorga_acceso_a_django_admin(self):
        usuario = User.objects.create_user(
            username='operario_sin_admin', is_operario=True,
        )
        self.client.force_login(usuario)

        response = self.client.get(reverse('admin:index'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_admin_permite_asignar_el_rol_is_operario(self):
        administrador = User.objects.create_superuser(
            username='admin_roles', password='clave-prueba',
        )
        self.client.force_login(administrador)

        response = self.client.get(reverse('admin:users_user_add'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="is_operario"')
