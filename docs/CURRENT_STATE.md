# Estado actual

Actualizado: 2026-10-15. Revisión documental del repositorio y de las fuentes académicas versionadas. No se modificó código de la aplicación.

## Implementación observada

- `Backend/` contiene un proyecto Django 6.1.2. `.python-version` solicita Python 3.14; `requirements.txt` fija Django, `asgiref`, `sqlparse`, `django-crispy-forms` y `crispy-bootstrap5`.
- La configuración local usa SQLite, `DEBUG=True` y una clave de desarrollo definida en settings. No es una configuración de producción.
- `main.operario` tiene el modelo `Comercio` y su administración. `main.users` extiende el usuario Django y agrega un vínculo a `Vehiculo`; existen migraciones iniciales.
- La página de seguimiento acepta códigos de demostración servidos desde `PEDIDOS_SIMULADOS` en memoria. No hay un modelo persistente de pedido ni un flujo de despacho implementado.
- La vista del repartidor requiere autenticación y renderiza una página básica. La ruta de operario intenta renderizar `hola.html`, que no existe en `Backend/templates/`.
- `Frontend/front` contiene solo un texto marcador; no hay un frontend separado implementado.
- Hay pruebas en `main/clienteFinal/tests.py`; las pruebas de otras aplicaciones son archivos vacíos o de plantilla. No se ejecutaron en esta revisión.

## Requisitos y planificación

Las fuentes versionadas describen siete épicas para comercios, pedidos, repartidores, despacho, operación móvil, consulta pública y auditoría. Son alcance planificado, no evidencia de funcionalidad terminada. El PGP organiza entregas entre el 9 de octubre y el 20 de noviembre de 2026; las fechas describen el plan, no el avance real del equipo.

La exportación Taiga derivada y versionada contiene 28 historias de usuario, 7 épicas y 2 hitos. Se omitieron las cuentas y la actividad del export privado original; no se consultó Taiga en vivo. Un documento previo de esta carpeta indicaba 29 historias; las fuentes disponibles no permiten explicar la diferencia. Confirmar cantidad y estado con el equipo o el tablero cuando corresponda.

`docs/context/` contiene copias de las cinco fuentes Word y una derivación sanitizada del JSON de Taiga. `docs/SOURCE_INDEX.md` identifica formato, alcance y limitaciones; `docs/DOCUMENTATION_WORKFLOW.md` describe la revisión posterior a pull y previa a push. Estos documentos nuevos no alteran la implementación.

## Verificaciones de esta revisión

- Project Init 1.0.0 inspeccionó el repositorio: rama `main`, estado limpio antes de esta tarea, stack detectado Python/Django.
- Project Init 1.0.0 copió las cinco fuentes Word sin sobrescribir documentos existentes y generó `scripts/check_docs.py` y `docs/DOCUMENTATION_WORKFLOW.md`. La exportación Taiga se sanitizó con el script versionado del proyecto y se verificó el recuento 7/28/2.
- `python3.14 -m django --version` no pudo ejecutarse: el intérprete disponible no tiene Django instalado. No se instalaron dependencias en el proyecto ni se ejecutaron `manage.py check` o las pruebas.
- Antes de editar se guardaron hashes de los 81 archivos rastreados. Después de documentar, los 71 archivos de código, recursos, dependencias y runtime comparados mantienen el mismo hash; los cambios restantes son documentación, `.gitignore` y el `CLAUDE.md` generado.

## Pendientes

- Confirmar historias y estado real con el tablero Taiga.
- Definir la interfaz frontend, la base de datos compartida y el despliegue.
- Completar el modelo y los flujos de pedidos según los requisitos aprobados.
- Resolver la plantilla faltante de la ruta de operario.
- Instalar las dependencias en un entorno de desarrollo del proyecto y ejecutar `manage.py check` y las pruebas existentes.
- Revisar claves, `DEBUG`, hosts, HTTPS y almacenamiento antes de cualquier uso de producción.
