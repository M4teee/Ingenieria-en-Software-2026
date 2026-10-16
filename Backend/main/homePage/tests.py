from django.test import TestCase, override_settings
from django.urls import reverse

from main.repartidor.models import Repartidor
from main.users.models import User


@override_settings(ALLOWED_HOSTS=['testserver'])
class PortadaYAccesosTests(TestCase):
    def test_portada_publica_muestra_entradas_de_cliente_y_repartidor(self):
        response = self.client.get(reverse('root'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, reverse('clienteFinal'))
        self.assertContains(response, reverse('repartidor_login_pin'))

    def test_operario_va_al_panel_y_no_al_admin(self):
        user = User.objects.create_user(username='operario_home', is_staff=True)
        self.client.force_login(user)

        response = self.client.get(reverse('root'))

        self.assertRedirects(response, reverse('operario:inicio'))

    def test_repartidor_va_a_su_panel(self):
        user = User.objects.create_user(username='repartidor_home')
        Repartidor.objects.create(user=user, pin='6543')
        self.client.force_login(user)

        response = self.client.get(reverse('root'))

        self.assertRedirects(response, reverse('repartidor'))
