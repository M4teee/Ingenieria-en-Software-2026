import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .views import debe_mostrar_tiempo

AHORA = datetime.datetime(2026, 10, 14, 15, 0, tzinfo=datetime.timezone.utc)


@override_settings(TIME_ZONE='America/Argentina/Buenos_Aires')
class SeguimientoTests(TestCase):
    def ver(self, codigo):
        return self.client.get(reverse('seguimiento', args=[codigo]))

    def test_en_viaje_muestra_estado_comercio_y_hora(self):
        # 15:00 UTC + 30 min = 15:30 UTC = 12:30 en Buenos Aires
        with patch('main.clienteFinal.views.timezone.now', return_value=AHORA):
            r = self.ver('viaje-demo')
        self.assertContains(r, 'En viaje')
        self.assertContains(r, 'Panadería Sol')
        self.assertContains(r, 'Llega aprox. a las 12:30')

    def test_estados_finales_ocultan_el_tiempo(self):
        for codigo, estado in [
            ('entregado-demo', 'Entregado'),
            ('fallido-demo', 'Fallido'),
            ('cancelado-demo', 'Cancelado'),
        ]:
            with self.subTest(codigo=codigo):
                r = self.ver(codigo)
                self.assertContains(r, estado)
                self.assertContains(r, 'Panadería Sol')
                self.assertNotContains(r, 'Llegada estimada')

    def test_estados_previos_no_muestran_tiempo(self):
        self.assertNotContains(self.ver('registrado-demo'), 'Llegada estimada')

    def test_codigo_inexistente_da_404(self):
        self.assertEqual(self.ver('no-existe').status_code, 404)

    def test_es_solo_lectura(self):
        r = self.client.post(reverse('seguimiento', args=['viaje-demo']))
        self.assertEqual(r.status_code, 405)

    def test_debe_mostrar_tiempo(self):
        self.assertTrue(debe_mostrar_tiempo('en_viaje', AHORA))
        self.assertFalse(debe_mostrar_tiempo('en_viaje', None))
        self.assertFalse(debe_mostrar_tiempo('entregado', AHORA))