# Ingeniería en Software 2026

Proyecto grupal de la materia Ingeniería en Software: desarrollo del Sistema de Gestión de Repartos (SGR), una aplicación web para organizar pedidos, coordinar repartidores y consultar el estado de las entregas.

## Estado actual

El repositorio contiene un backend Django y documentación académica. Los operarios con `is_staff` pueden registrar pedidos persistidos asociados a comercios activos; seguimiento público e historial consultan esos mismos pedidos. El repartidor puede avanzar el estado de pedidos que ya le fueron asignados. `Frontend/front` es solo un marcador de posición; las páginas disponibles están en plantillas Django.

La estructura y las funcionalidades presentes se describen en [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md). Los requisitos y sus fuentes están resumidos en [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) y [`docs/SOURCE_INDEX.md`](docs/SOURCE_INDEX.md). La preparación, pruebas y recorrido manual están en [`docs/GUIA-EJECUCION-Y-PRUEBAS.md`](docs/GUIA-EJECUCION-Y-PRUEBAS.md); el mapa técnico está en [`docs/TOUR-APLICACION.md`](docs/TOUR-APLICACION.md).

## Tecnologías declaradas

- Python 3.14, según `.python-version`.
- Django 6.1.2.
- SQLite en la configuración local inicial.
- `django-crispy-forms` y `crispy-bootstrap5`.
- Pillow para el procesamiento de fotografías.
- Interfaz web basada en plantillas Django; no se definió una tecnología separada para `Frontend/`.
- La Entrevista 02 describe PC web o escritorio para el operario y web móvil para el repartidor; la plataforma/arquitectura elegida por el equipo sigue pendiente.

## Preparar y ejecutar el backend

Se necesita Python 3.14 y `pip`. Desde la raíz del proyecto:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd Backend
python manage.py check
python manage.py migrate
python manage.py runserver
```

Abrí la dirección local que muestra Django, normalmente `http://127.0.0.1:8000/`. `migrate` crea o actualiza la base SQLite local; el archivo está excluido de Git. `runserver` es para desarrollo, no para producción. Para salir, detené el servidor con `Ctrl+C` y ejecutá `deactivate`.

Después de ejecutar las migraciones, la carga está en `/operario/pedidos/nuevo/`; el seguimiento público usa `/clienteFinal/seguimiento/<codigo>/`. No existe todavía una pantalla para asignar pedidos a repartidores. Las instrucciones anteriores son para desarrollo y no implican que la configuración sea apta para producción.

## Estructura

- `Backend/`: configuración, aplicaciones Django, migraciones, plantillas y recursos estáticos.
- `Frontend/`: espacio reservado sin implementación propia.
- `docs/`: brief, estado, decisiones, fuentes académicas versionadas y workflow documental.
- `requirements.txt`: dependencias Python fijadas.

Antes de iniciar una tarea, consultá [`docs/INDEX.md`](docs/INDEX.md). Las fuentes y sus límites están descritos en [`docs/SOURCE_INDEX.md`](docs/SOURCE_INDEX.md); el workflow de actualización está en [`docs/DOCUMENTATION_WORKFLOW.md`](docs/DOCUMENTATION_WORKFLOW.md).
