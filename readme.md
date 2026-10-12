# Ingeniería en Software 2026

Aplicación grupal de la materia Ingeniería en Software. El repositorio reúne el código y la documentación de trabajo aprobada por el equipo.

## Tecnologías iniciales

- Backend: Python 3.13 y Django 5.2 LTS.
- Base de datos de arranque: SQLite, creada localmente por Django.
- Frontend: pendiente de acordar según las historias de usuario y la arquitectura aprobada.
- Repositorio y revisión de cambios: GitHub.

La configuración inicial de SQLite permite poner en marcha Django. Antes de desarrollar funcionalidades que dependan de datos compartidos, el equipo debe acordar PostgreSQL local y el proveedor gratuito de despliegue (Neon o Supabase), procurando usar el mismo motor en desarrollo y producción.

## Requisitos

- Git.
- Python 3.13 instalado en el sistema. En macOS se puede instalar desde [Python.org](https://www.python.org/downloads/release/python-31316/).

En macOS es normal que el comando `python` no exista antes de activar un entorno virtual. Para crear el entorno se usa `python3.13`; una vez activado, el entorno agrega `python` y apunta a la versión aislada del proyecto.

## Preparar el entorno en macOS

Desde la carpeta raíz del repositorio:

```bash
python3.13 --version
python3.13 -m pip --version
python3.13 -m venv .venv
```

Activá el entorno según la terminal que uses:

```bash
# Bash o Zsh (por ejemplo, Terminal de macOS configurada con Zsh)
source .venv/bin/activate
```

```fish
# Fish
source .venv/bin/activate.fish
```

Después de activarlo:

```bash
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

El primer comando debería mostrar Python 3.13.x. Después de activar `.venv`, `python --version` también debería mostrar Python 3.13.x. El prefijo `(.venv)` en la terminal indica que el entorno está activo.

## Ejecutar Django

Con `.venv` activo:

```bash
cd Backend
python manage.py check
python manage.py migrate
python manage.py runserver
```

Abrí la dirección que muestra la terminal, normalmente <http://127.0.0.1:8000/>. `runserver` es solo para desarrollo local. Para salir, presioná `Ctrl+C`; para desactivar el entorno, ejecutá `deactivate`.

Si agregás una dependencia de Python, instalala con `python -m pip install nombre-del-paquete` dentro de `.venv` y actualizá `requirements.txt` desde la raíz:

```bash
python -m pip freeze > requirements.txt
```

## Estructura

```text
Backend/
  manage.py             Comandos de Django
  config/               Configuración general, URL y servidores ASGI/WSGI
Frontend/               Espacio reservado; tecnología pendiente de acordar
docs/                   Contexto, fuentes, decisiones y estado del proyecto
requirements.txt        Dependencias Python del backend
```

Las aplicaciones Django del dominio se agregarán dentro de `Backend/` cuando se hayan agrupado las historias de usuario en áreas funcionales. Las carpetas `Backend/back` y `Frontend/front` que ya existían se conservaron.

## Trabajo en equipo

1. Actualizá la rama principal antes de empezar: `git switch main` y `git pull`.
2. Creá una rama por historia o tarea, por ejemplo `feat/us-12-registro-campo`.
3. Hacé commits pequeños y descriptivos; subí la rama y abrí una pull request para revisión.
4. Después de integrar los cambios, actualizá el estado de la historia en Taiga.

No subas `.venv/`, secretos, archivos `.env`, ni la base de datos local `db.sqlite3`. No guardes tokens o contraseñas en el repositorio.

## Documentación de contexto

Los archivos de `docs/` permiten retomar el proyecto sin depender del historial de una conversación. La consigna y los documentos aprobados siguen siendo las fuentes de autoridad; los resúmenes de IA deben conservar referencias y revisarse antes de aprobarlos. Ver [docs/](docs/).
