# Ingeniería en Software 2026

Proyecto grupal de la materia Ingeniería en Software: desarrollo del Sistema de Gestión de Repartos (SGR), una aplicación web para organizar pedidos, coordinar repartidores y consultar el estado de las entregas.

## Estado actual

El repositorio contiene una base de backend Django y documentación académica. Hay modelos iniciales de comercios, usuarios y vehículos, administración de comercios y una pantalla de seguimiento con pedidos simulados. Todavía no existe un modelo persistente de pedido ni un flujo completo de asignación y entrega. `Frontend/front` es solo un marcador de posición; las páginas disponibles están en las plantillas Django.

La estructura y las funcionalidades presentes se describen en [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md). Los requisitos y sus fuentes están resumidos en [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) y [`docs/SOURCE_INDEX.md`](docs/SOURCE_INDEX.md).

## Tecnologías declaradas

- Python 3.14, según `.python-version`.
- Django 6.1.2.
- SQLite en la configuración local inicial.
- `django-crispy-forms` y `crispy-bootstrap5`.
- Interfaz web basada en plantillas Django; no se definió una tecnología separada para `Frontend/`.

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

El flujo de `/operario/` todavía renderiza `hola.html`, plantilla que no está en el árbol actual. No se verificó la aplicación en este entorno: el Python 3.14 disponible no tiene Django instalado. Las instrucciones anteriores describen cómo preparar una instalación limpia; no implican que todas las rutas estén completas.

## Estructura

- `Backend/`: configuración, aplicaciones Django, migraciones, plantillas y recursos estáticos.
- `Frontend/`: espacio reservado sin implementación propia.
- `docs/`: brief, estado, decisiones, fuentes académicas versionadas y workflow documental.
- `requirements.txt`: dependencias Python fijadas.

Antes de iniciar una tarea, consultá [`docs/INDEX.md`](docs/INDEX.md). Las fuentes y sus límites están descritos en [`docs/SOURCE_INDEX.md`](docs/SOURCE_INDEX.md); el workflow de actualización está en [`docs/DOCUMENTATION_WORKFLOW.md`](docs/DOCUMENTATION_WORKFLOW.md).
