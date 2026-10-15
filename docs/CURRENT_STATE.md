# Estado actual

Actualizado: 2026-10-15. Implementación de la HU #18 ("Aceptar asignacion de pedidos") en `main.repartidor`; no se modificó `clienteFinal`, `operario` ni `users`.

## Implementación observada

- `Backend/` contiene un proyecto Django 6.1.2. `.python-version` solicita Python 3.14; `requirements.txt` fija Django, `asgiref`, `sqlparse`, `django-crispy-forms` y `crispy-bootstrap5`.
- La configuración local usa SQLite, `DEBUG=True` y una clave de desarrollo definida en settings. No es una configuración de producción.
- `main.operario` tiene el modelo `Comercio` y su administración. `main.users` extiende el usuario Django y agrega un vínculo a `Vehiculo`; existen migraciones iniciales.
- `main.repartidor` agrega (migración `0001_initial`): `RepartidorPerfil` (OneToOne con `User`, campo `disponible`), `Pedido` (FK a `Comercio` y a `User`, estado con choices `registrado/asignado/retirado/en_viaje/entregado/fallido/cancelado`, `fecha_hora_asignacion`) e `HistorialPedido` (auditoría por pedido). No existían modelos previos de pedido ni de historial; los de repartidor y de `clienteFinal` siguen siendo datos simulados en memoria.
- HU #18 implementada en `main.repartidor`: la vista `home` muestra el pedido asignado con cuenta regresiva de 300 segundos (JS propio en `templates/repartidor/index.html`, hereda `base.html`); `aceptar` confirma el pedido a `retirado` y registra el evento en el historial; `rechazar` libera el pedido a `registrado`, registra "Rechazado por repartidor [Nombre]" y marca al repartidor no disponible; la expiración de los 5 minutos se evalúa de forma perezosa al cargar `home` y al procesar aceptar/rechazar (libera el pedido y marca al repartidor no disponible). Las vistas de aceptar/rechazar usan `transaction.atomic()` + `select_for_update()` y requieren POST.
- La página de seguimiento de `clienteFinal` sigue con `PEDIDOS_SIMULADOS` en memoria; aún no consume el modelo `Pedido` nuevo.
- La ruta de operario sigue intentando renderizar `hola.html`, que no existe en `Backend/templates/`.
- `Frontend/front` contiene solo un texto marcador; no hay un frontend separado implementado.

## Requisitos y planificación

Las fuentes versionadas describen siete épicas para comercios, pedidos, repartidores, despacho, operación móvil, consulta pública y auditoría. Son alcance planificado, no evidencia de funcionalidad terminada. El PGP organiza entregas entre el 9 de octubre y el 20 de noviembre de 2026; las fechas describen el plan, no el avance real del equipo.

La exportación Taiga derivada y versionada contiene 28 historias de usuario, 7 épicas y 2 hitos. Se omitieron las cuentas y la actividad del export privado original; no se consultó Taiga en vivo. Un documento previo de esta carpeta indicaba 29 historias; las fuentes disponibles no permiten explicar la diferencia. Confirmar cantidad y estado con el equipo o el tablero cuando corresponda.

`docs/context/` contiene copias de las cinco fuentes Word y una derivación sanitizada del JSON de Taiga. `docs/SOURCE_INDEX.md` identifica formato, alcance y limitaciones; `docs/DOCUMENTATION_WORKFLOW.md` describe la revisión posterior a pull y previa a push. Estos documentos nuevos no alteran la implementación.

## Verificaciones de esta revisión

- Ejecutado en la rama `hu18-repartidor` con el venv del repositorio (Python 3.14.7, Django 6.1.2), desde `Backend/`:
  - `manage.py makemigrations` (generó `main/repartidor/migrations/0001_initial.py`) y `manage.py migrate`: OK.
  - `manage.py makemigrations --check --dry-run`: "No changes detected".
  - `manage.py test` (suite completa): 26 pruebas, OK en ~14 s. Incluye 16 pruebas nuevas de `main.repartidor` (aceptación en tiempo, rechazo explícito, expiración a los 300 segundos, seguridad) y las 10 existentes de `clienteFinal` (no se modificaron).
- `python3 scripts/check_docs.py .` desde la raíz del repositorio: OK, sin enlaces rotos ni rutas específicas de máquina.
- Project Init 1.0.0 inspeccionó el repositorio (ver git log previo) y generó `scripts/check_docs.py` y `docs/DOCUMENTATION_WORKFLOW.md`.

## Pendientes

- Confirmar historias y estado real con el tablero Taiga.
- Definir la interfaz frontend, la base de datos compartida y el despliegue.
- Integrar el modelo `Pedido` con el seguimiento de `clienteFinal` y el flujo de asignación del operario (la asignación inicial no tiene vista: los pedidos se asignan por admin o por código).
- La expiración de los 5 minutos es perezosa (se evalúa al cargar la vista o al aceptar/rechazar); si se necesita liberación inmediata sin interacción, hace falta una tarea programada (celery/cron).
- Resolver la plantilla faltante de la ruta de operario.
- Revisar claves, `DEBUG`, hosts, HTTPS y almacenamiento antes de cualquier uso de producción.
