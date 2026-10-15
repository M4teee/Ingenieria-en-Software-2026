# Decisiones y temas abiertos

Este registro conserva el estado que ya estaba anotado y separa los hechos del repositorio de los acuerdos del equipo. No atribuir una decisión a una persona si la fuente no lo hace.

## Decisiones registradas

| Fecha registrada | Tema | Estado |
|---|---|---|
| 2026-10-11 | Python 3.14.8 para el entorno de trabajo | Registrada como acordada en la documentación previa. `.python-version` especifica la serie `3.14`, no el parche. |
| 2026-10-11 | Django 6.1.2 | Registrada como versión elegida para el backend. |

## Hechos de configuración, no decisiones de arquitectura

- `Backend/config/settings.py` configura SQLite para desarrollo local.
- `requirements.txt` fija las versiones actuales de Django y sus dependencias.
- `Frontend/` sigue siendo un marcador de posición; no hay framework elegido en sus archivos.

## Pendiente de confirmación del equipo

- Base de datos compartida y proveedor; PostgreSQL figuraba como propuesta previa, no como acuerdo.
- Arquitectura y tecnologías de la interfaz.
- Despliegue, seguridad de producción y manejo de archivos/fotografías.
- Alcance y prioridad de las historias y fechas vigentes de los sprints.

Al cerrar una decisión, agregá fecha, contexto, opciones consideradas, acuerdo y fuente o acta que lo respalda.
