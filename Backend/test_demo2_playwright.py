import os
import sys
from pathlib import Path

# Setup paths
APP_DIR = Path(r"C:\Users\simor\Documents\Ing\Tercero\Segundo cuatri\Software\Ingenieria-en-Software-2026\Backend")
sys.path.insert(0, str(APP_DIR))
os.chdir(str(APP_DIR))

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings_test"
os.environ["DATABASE_URL"] = ""

import django
django.setup()

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from main.users.models import User
from main.operario.models import Comercio, Devolucion
from main.repartidor.models import Pedido, HistorialEstado, Repartidor
from playwright.sync_api import sync_playwright

class Demo2PlaywrightTest(StaticLiveServerTestCase):
    port = 8888

    def setUp(self):
        super().setUp()
        # Seed Demo 2 data
        # 1. Operario
        self.operario = User.objects.create_user(
            username='admin',
            password='operario',
            is_staff=True,
            is_operario=True,
        )

        # 2. Comercios 1 to 9
        self.comercios = {}
        for i in range(1, 10):
            self.comercios[f"Comercio {i}"] = Comercio.objects.create(
                nombre=f"Comercio {i}",
                direccion=f"Avenida {i} nro. {i*1111}",
                contacto=f"221 {i*111}-{i*1111}",
                activo=True
            )

        # 3. Repartidores
        # bicicleta 1..3, moto 1..3, auto 1..3, camion 1..3
        reps_data = [
            ('bicicleta1', 'bicicleta', '1111', True),
            ('bicicleta2', 'bicicleta', '1222', True),
            ('bicicleta3', 'bicicleta', '1333', False),
            ('moto1', 'moto', '2111', False),
            ('moto2', 'moto', '2222', True),
            ('moto3', 'moto', '2333', False),
            ('auto1', 'auto', '3111', True),
            ('auto2', 'auto', '3222', True),
            ('auto3', 'auto', '3333', False),
            ('camion1', 'camion', '4111', False),
            ('camion2', 'camion', '4222', False),
            ('camion3', 'camion', '4333', False),
        ]
        self.reps = {}
        for uname, veh, pin, disp in reps_data:
            u = User.objects.create_user(username=uname)
            r = Repartidor.objects.create(
                user=u,
                vehiculo=veh,
                pin=pin,
                disponible=disp,
                disponible_desde=timezone.now() if disp else None
            )
            self.reps[uname] = r

        # 4. Dummy photo
        dummy_img = SimpleUploadedFile("foto.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9", content_type="image/jpeg")

        # 5. Pedidos
        # DEMO20010 entregado con foto
        p10 = Pedido.objects.create(
            codigo='DEMO20010',
            comercio=self.comercios['Comercio 1'],
            repartidor=self.reps['camion1'].user,
            estado='entregado',
            vehiculo_requerido='camion',
            direccion_destino='Destino 10',
            datos_destinatario='Destinatario 10',
            tamano_paquete='Grande',
            fecha_hora_estimada_entrega=timezone.now() + timezone.timedelta(hours=2)
        )
        HistorialEstado.objects.create(
            pedido=p10,
            estado_anterior='',
            estado_nuevo='registrado',
            usuario=self.operario,
            incidencia='Alta de pedido'
        )
        HistorialEstado.objects.create(
            pedido=p10,
            estado_anterior='registrado',
            estado_nuevo='entregado',
            usuario=self.reps['camion1'].user,
            incidencia='Entrega exitosa',
            fotografia=dummy_img
        )

        # DEMO20012 fallido con foto
        p12 = Pedido.objects.create(
            codigo='DEMO20012',
            comercio=self.comercios['Comercio 3'],
            repartidor=self.reps['camion3'].user,
            estado='fallido',
            vehiculo_requerido='camion',
            direccion_destino='Destino 12',
            datos_destinatario='Destinatario 12',
            tamano_paquete='Pesado',
            fecha_hora_estimada_entrega=timezone.now() + timezone.timedelta(hours=2)
        )
        HistorialEstado.objects.create(
            pedido=p12,
            estado_anterior='',
            estado_nuevo='registrado',
            usuario=self.operario,
            incidencia='Alta de pedido'
        )
        HistorialEstado.objects.create(
            pedido=p12,
            estado_anterior='registrado',
            estado_nuevo='fallido',
            usuario=self.reps['camion3'].user,
            incidencia='Destinatario ausente',
            fotografia=dummy_img
        )

        # DEMO20013 en_viaje
        p13 = Pedido.objects.create(
            codigo='DEMO20013',
            comercio=self.comercios['Comercio 4'],
            repartidor=self.reps['moto1'].user,
            estado='en_viaje',
            vehiculo_requerido='moto',
            direccion_destino='Destino 13',
            datos_destinatario='Destinatario 13',
            tamano_paquete='Chico',
            fecha_hora_estimada_entrega=timezone.now() + timezone.timedelta(hours=2)
        )
        HistorialEstado.objects.create(
            pedido=p13,
            estado_anterior='',
            estado_nuevo='registrado',
            usuario=self.operario,
            incidencia='Alta de pedido'
        )
        HistorialEstado.objects.create(
            pedido=p13,
            estado_anterior='registrado',
            estado_nuevo='en_viaje',
            usuario=self.reps['moto1'].user,
            incidencia='Viaje iniciado'
        )

        self.p10_pk = p10.pk
        self.p12_pk = p12.pk
        self.p13_pk = p13.pk
        self.c3_pk = self.comercios['Comercio 3'].pk
        self.camion1_user_pk = self.reps['camion1'].user.pk
        self.camion3_rep_pk = self.reps['camion3'].pk

    def test_playwright_e2e_messages_and_flows(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page_op = browser.new_page()
            page_rep = browser.new_page()

            base_url = self.live_server_url
            print(f"Testing against live server: {base_url}")

            # -------------------------------------------------------------
            # Operario Login (HU 9 / Verification of is_operario)
            # -------------------------------------------------------------
            page_op.goto(f"{base_url}/login/")
            page_op.fill("input[name='username']", "admin")
            page_op.fill("input[name='password']", "operario")
            page_op.click("button[type='submit']")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("/operario/", page_op.url)
            print("✓ Operario login successful")

            # -------------------------------------------------------------
            # HU 15: Repartidores listado y vehículos
            # -------------------------------------------------------------
            page_op.goto(f"{base_url}/operario/repartidores/")
            text = page_op.content()
            self.assertIn("Personal de reparto", text)
            self.assertIn("bicicleta1", text)
            self.assertIn("camion1", text)
            print("✓ HU 15 Esc. 1 verified: Repartidores list view")

            # -------------------------------------------------------------
            # HU 25: Editar comercio (Éxito y duplicado)
            # -------------------------------------------------------------
            c1_pk = self.comercios['Comercio 1'].pk
            page_op.goto(f"{base_url}/operario/comercios/{c1_pk}/editar/")
            page_op.fill("input[name='direccion']", "Nueva Direccion 123")
            page_op.click("button:has-text('Guardar cambios')")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Datos del comercio actualizados", page_op.content())
            print("✓ HU 25 Esc. 1 verified: 'Datos del comercio actualizados'")

            # Escenario 2: nombre duplicado
            page_op.fill("input[name='nombre']", "Comercio 2")
            page_op.click("button:has-text('Guardar cambios')")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Ya existe un comercio registrado con ese nombre", page_op.content())
            print("✓ HU 25 Esc. 2 verified: 'Ya existe un comercio registrado con ese nombre'")

            # -------------------------------------------------------------
            # HU 16 & 27: Deshabilitar y reactivar comercio
            # -------------------------------------------------------------
            page_op.goto(f"{base_url}/operario/comercios/")
            page_op.wait_for_load_state("networkidle")

            # Escenario 2 HU 16: cancelar diálogo de confirmación
            page_op.once("dialog", lambda dialog: dialog.dismiss())
            switch_c3 = page_op.locator("input[data-nombre='Comercio 3']")
            switch_c3.click()
            page_op.wait_for_timeout(500)
            self.assertTrue(switch_c3.is_checked())
            print("✓ HU 16 Esc. 2 verified: cancel confirmation leaves switch checked")

            # Escenario 1 HU 16: confirmar deshabilitación
            page_op.once("dialog", lambda dialog: dialog.accept())
            switch_c3.click()
            page_op.wait_for_timeout(500)
            page_op.wait_for_selector("#mensaje-estado-comercio:not(.d-none)")
            msg_c = page_op.locator("#mensaje-estado-comercio").text_content()
            self.assertIn("Comercio deshabilitado exitosamente", msg_c)
            print("✓ HU 16 Esc. 1 verified: 'Comercio deshabilitado exitosamente'")

            # Escenario 1 HU 27: reactivar comercio
            page_op.once("dialog", lambda dialog: dialog.accept())
            switch_c3.click()
            page_op.wait_for_selector("#mensaje-estado-comercio:not(.d-none)")
            msg_r = page_op.locator("#mensaje-estado-comercio").text_content()
            self.assertIn("Comercio reactivado exitosamente", msg_r)
            print("✓ HU 27 Esc. 1 verified: 'Comercio reactivado exitosamente'")

            # -------------------------------------------------------------
            # HU 28: Buscar comercio sin coincidencias
            # -------------------------------------------------------------
            page_op.fill("#buscar-comercio", "ComercioInexistente1234")
            page_op.wait_for_selector("#sin-resultados-comercios:not([hidden])")
            no_com_msg = page_op.locator("#sin-resultados-comercios").text_content()
            self.assertIn("No se encontraron comercios con ese nombre.", no_com_msg)
            print("✓ HU 28 Esc. 2 verified: 'No se encontraron comercios con ese nombre.'")

            # -------------------------------------------------------------
            # HU 23: Filtrar historial general
            # -------------------------------------------------------------
            page_op.goto(f"{base_url}/operario/pedidos/historial/?comercio=Comercio+3&estado=fallido")
            self.assertIn("DEMO20012", page_op.content())
            print("✓ HU 23 Esc. 1 verified: filter found DEMO20012")

            page_op.goto(f"{base_url}/operario/pedidos/historial/?comercio=Comercio+3&estado=cancelado")
            self.assertIn("No se encontraron pedidos que coincidan con los filtros ingresados", page_op.content())
            print("✓ HU 23 Esc. 2 verified: 'No se encontraron pedidos que coincidan con los filtros ingresados'")

            # -------------------------------------------------------------
            # HU 34: Entregas fallidas y confirmar devolución
            # -------------------------------------------------------------
            page_op.goto(f"{base_url}/operario/pedidos/fallidos/")
            self.assertIn("DEMO20012", page_op.content())
            # Confirmar devolución
            page_op.click("button:has-text('Confirmar devolución')")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Devolución registrada", page_op.content())
            print("✓ HU 34 Esc. 2 verified: 'Devolución registrada'")

            # -------------------------------------------------------------
            # HU 14: Ver historial/timeline con fotos ampliables
            # -------------------------------------------------------------
            page_op.goto(f"{base_url}/operario/pedidos/{self.p10_pk}/")
            self.assertIn("Historial del pedido", page_op.content())
            modal_trigger = page_op.locator("a[data-bs-target='#modalEvidencia']").first
            self.assertTrue(modal_trigger.is_visible())
            print("✓ HU 14 verified: Timeline and photo thumbnail modal trigger")

            # -------------------------------------------------------------
            # HU 30, 33, 42: Crear pedido sin candidato, alerta y reintento fallido
            # -------------------------------------------------------------
            page_op.goto(f"{base_url}/operario/pedidos/nuevo/")
            page_op.select_option("select[name='comercio']", label="Comercio 1")
            page_op.fill("input[name='direccion_destino']", "Calle Falsa 123")
            page_op.fill("textarea[name='datos_destinatario']", "Cliente Uno")
            page_op.fill("textarea[name='tamano_paquete']", "Mediano")
            page_op.select_option("select[name='vehiculo_requerido']", value="camion")
            page_op.fill("textarea[name='especificaciones_traslado']", "Ninguna")
            # Set datetime 2 hours in the future
            futuro = (timezone.localtime() + timezone.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')
            page_op.fill("input[name='fecha_hora_estimada_entrega']", futuro)
            page_op.click("button:has-text('Registrar pedido')")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Pedido registrado con éxito", page_op.content())

            # Ir al panel de pedidos para ver la alerta de pedido sin repartidor
            page_op.goto(f"{base_url}/operario/")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Pedido sin repartidor disponible", page_op.content())
            print("✓ HU 30 Esc. 1 verified: 'Pedido sin repartidor disponible' in dashboard")

            # Abrir el detalle del pedido desde la alerta
            page_op.click("#alerta-sin-repartidor a")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Sin asignar", page_op.content())
            self.assertIn("Pedido sin repartidor disponible", page_op.content())
            print("✓ HU 33 Esc. 2 verified: 'Sin asignar' in detail")

            # HU 42 Esc. 2: Reintentar sin candidatos
            btn_reintentar = page_op.locator("button:has-text('Reintentar asignación')").first
            btn_reintentar.click()
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Pedido sin repartidor disponible", page_op.content())
            print("✓ HU 42 Esc. 2 verified: Retry without candidates keeps alert")

            # -------------------------------------------------------------
            # HU 15 Esc. 2: Repartidor camion1 se pone Disponible desde móvil
            # -------------------------------------------------------------
            page_rep.goto(f"{base_url}/repartidor/login-pin/")
            page_rep.fill("input[name='pin']", "4111")
            page_rep.click("button[type='submit']")
            page_rep.wait_for_load_state("networkidle")
            self.assertIn("/repartidor/", page_rep.url)

            # Cambiar a disponible
            page_rep.click("button:has-text('Marcarme disponible')")
            page_rep.wait_for_load_state("networkidle")
            self.assertIn("Marcarme no disponible", page_rep.content())
            print("✓ Repartidor camion1 is now Disponible")

            # HU 42 Esc. 1: Operario reintenta asignación y asigna a camion1
            btn_reintentar2 = page_op.locator("button:has-text('Reintentar asignación')").first
            btn_reintentar2.click()
            page_op.wait_for_load_state("networkidle")
            self.assertIn("camion1", page_op.content())
            print("✓ HU 42 Esc. 1 verified: Order assigned to camion1 upon retry")

            # -------------------------------------------------------------
            # HU 29 Esc. 2: Deshabilitación bloqueada por viaje en curso
            # -------------------------------------------------------------
            page_op.goto(f"{base_url}/operario/repartidores/")
            page_op.wait_for_load_state("networkidle")
            # Listen for alert
            alert_msg = []
            page_op.once("dialog", lambda dialog: [alert_msg.append(dialog.message), dialog.accept()])
            switch_rep = page_op.locator("input[data-username='camion1']")
            switch_rep.click()
            page_op.wait_for_timeout(1000)
            self.assertTrue(len(alert_msg) > 0)
            self.assertIn("El repartidor tiene pedidos en curso", alert_msg[0])
            print("✓ HU 29 Esc. 2 verified: 'El repartidor tiene pedidos en curso' dialog")

            # -------------------------------------------------------------
            # HU 13: Cancelar pedido asignado
            # -------------------------------------------------------------
            page_op.go_back() # returns to pedido detail
            page_op.wait_for_load_state("networkidle")
            page_op.once("dialog", lambda dialog: dialog.accept())
            page_op.click("button:has-text('Cancelar pedido')")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Cancelado", page_op.content())
            print("✓ HU 13 verified: Order cancelled successfully")

            # -------------------------------------------------------------
            # HU 32: Regenerar PIN con ingreso explícito (Esc. 1, 2, 3, 4)
            # -------------------------------------------------------------
            rep3_pk = self.camion3_rep_pk
            page_op.goto(f"{base_url}/operario/repartidores/")
            page_op.wait_for_load_state("networkidle")

            # Escenario 2: Formato inválido (< 4 dígitos o no numérico)
            page_op.click(f"button[data-bs-target='#modalPin{rep3_pk}']")
            page_op.wait_for_selector(f"#modalPin{rep3_pk}.show")
            page_op.fill(f"#pinInput{rep3_pk}", "12")
            page_op.click(f"#modalPin{rep3_pk} button[type='submit']")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("El PIN debe ser numérico y de exactamente 4 dígitos.", page_op.content())
            print("✓ HU 32 Esc. 2 verified: 'El PIN debe ser numérico y de exactamente 4 dígitos.'")

            # Escenario 3: PIN ya asignado a otro repartidor
            page_op.click(f"button[data-bs-target='#modalPin{rep3_pk}']")
            page_op.wait_for_selector(f"#modalPin{rep3_pk}.show")
            page_op.fill(f"#pinInput{rep3_pk}", "1111") # asignado a bicicleta1
            page_op.click(f"#modalPin{rep3_pk} button[type='submit']")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Ese PIN ya está asignado a otro repartidor.", page_op.content())
            print("✓ HU 32 Esc. 3 verified: 'Ese PIN ya está asignado a otro repartidor.'")

            # Escenario 4: Mismo PIN actual
            page_op.click(f"button[data-bs-target='#modalPin{rep3_pk}']")
            page_op.wait_for_selector(f"#modalPin{rep3_pk}.show")
            page_op.fill(f"#pinInput{rep3_pk}", "4333") # actual de camion3
            page_op.click(f"#modalPin{rep3_pk} button[type='submit']")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("El nuevo PIN debe ser diferente al actual.", page_op.content())
            print("✓ HU 32 Esc. 4 verified: 'El nuevo PIN debe ser diferente al actual.'")

            # Escenario 1: PIN válido y confirmación
            page_op.click(f"button[data-bs-target='#modalPin{rep3_pk}']")
            page_op.wait_for_selector(f"#modalPin{rep3_pk}.show")
            page_op.fill(f"#pinInput{rep3_pk}", "9876")
            page_op.click(f"#modalPin{rep3_pk} button[type='submit']")
            page_op.wait_for_load_state("networkidle")
            self.assertIn("Transmití este PIN al repartidor. El PIN anterior ya no permite ingresar.", page_op.content())
            self.assertIn("9876", page_op.content())
            print("✓ HU 32 Esc. 1 verified: 'Transmití este PIN al repartidor. El PIN anterior ya no permite ingresar.'")

            # Verificación de login móvil con PIN viejo y nuevo
            page_rep.click("button:has-text('Cerrar sesión')")
            page_rep.wait_for_load_state("networkidle")

            page_rep.goto(f"{base_url}/repartidor/login-pin/")
            page_rep.fill("input[name='pin']", "4333") # viejo
            page_rep.click("button:has-text('Ingresar')")
            page_rep.wait_for_load_state("networkidle")
            self.assertIn("PIN incorrecto. Verifique los dígitos", page_rep.content())
            print("✓ HU 32 Esc. 1 login verified: PIN anterior invalidado con 'PIN incorrecto. Verifique los dígitos'")

            page_rep.fill("input[name='pin']", "9876") # nuevo
            page_rep.click("button:has-text('Ingresar')")
            page_rep.wait_for_load_state("networkidle")
            self.assertIn("/repartidor/", page_rep.url)
            print("✓ HU 32 Esc. 1 login verified: PIN nuevo autentica correctamente")

            # -------------------------------------------------------------
            # HU 29 Esc. 1: Deshabilitar repartidor sin viajes en curso
            # -------------------------------------------------------------
            page_op.goto(f"{base_url}/operario/repartidores/")
            page_op.wait_for_load_state("networkidle")
            switch_rep3 = page_op.locator("input[data-username='camion3']")
            switch_rep3.click()
            page_op.wait_for_timeout(1000)
            self.assertFalse(switch_rep3.is_checked())
            print("✓ HU 29 Esc. 1 verified: camion3 switch disabled")

            # Repartidor deshabilitado no puede ingresar
            page_rep.click("button:has-text('Cerrar sesión')")
            page_rep.wait_for_load_state("networkidle")

            page_rep.goto(f"{base_url}/repartidor/login-pin/")
            page_rep.fill("input[name='pin']", "9876")
            page_rep.click("button:has-text('Ingresar')")
            page_rep.wait_for_load_state("networkidle")
            self.assertIn("PIN incorrecto. Verifique los dígitos", page_rep.content())
            print("✓ HU 29 Esc. 1 verified: Disabled repartidor PIN cannot login")

            browser.close()
            print("🎉 ALL SPRINT 2 PLAYWRIGHT TESTS PASSED!")

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    # Run test
    test_case = Demo2PlaywrightTest()
    # Use django test runner
    from django.test.runner import DiscoverRunner
    runner = DiscoverRunner(verbosity=2)
    suite = runner.build_suite(test_labels=['test_demo2_playwright.Demo2PlaywrightTest'])
    runner.setup_databases()
    runner.setup_test_environment()
    results = runner.run_suite(suite)
    runner.teardown_test_environment()
    runner.teardown_databases(None)
    sys.exit(bool(results.failures or results.errors))
