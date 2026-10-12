# Estado actual

Actualizado: 2026-10-11. Se actualizó el entorno base a Django 6.1.2 y Python 3.14.8. Python 3.15.0 ya está publicado, pero Django 6.1 todavía declara soporte hasta Python 3.14; se priorizó una combinación oficialmente compatible. La instalación local se recreó con Python 3.14.8.

## Situación observada

- Existe una base mínima de backend Django en `Backend/`, con configuración en `Backend/config/` y `manage.py`.
- `AGENTS.md` y `docs/INDEX.md` orientan la lectura y el mantenimiento del contexto del proyecto.
- `requirements.txt` fija Django 6.1.2 y sus dependencias; `.python-version` indica la serie Python 3.14.
- `Backend/back` y `Frontend/front` son espacios reservados. No se encontró una aplicación de dominio ni una implementación de frontend en el contenido versionado.
- La configuración inicial usa SQLite; la base local existente se mantiene como archivo ignorado y no forma parte de estos cambios documentales.
- El brief, las fuentes de requisitos y varias decisiones siguen incompletos o pendientes de confirmación, según `SOURCE_INDEX.md`, `PROJECT_BRIEF.md` y `DECISIONS.md`.

## Pendientes conocidos

1. Incorporar o enlazar la consigna, presentaciones, entrevistas, requerimientos, PGP e iniciativas/épicas en `SOURCE_INDEX.md`.
2. Completar y validar el brief y la base de conocimiento usando las fuentes originales.
3. Confirmar con el equipo las versiones de Python y Django, el motor de base de datos, el frontend y la estrategia de despliegue.
4. Registrar el tablero Taiga y actualizar planificación, historias y sprints a partir de su estado vigente.
5. Crear las aplicaciones y funcionalidades del dominio cuando el alcance esté aprobado.

## Verificaciones

Se instaló el entorno desde `requirements.txt` usando Python 3.14.8. La versión de Django y las versiones instaladas se comprobaron después de la instalación. No se ejecutaron pruebas de la aplicación.

## Archivos locales fuera del control de versiones

Los artefactos locales ignorados —como el entorno virtual, la base SQLite, cachés de Python y `.DS_Store`— no forman parte de los cambios documentales ni deben subirse al repositorio. Las decisiones técnicas y fuentes que figuran como pendientes continúan requiriendo confirmación del equipo.
