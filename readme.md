# Ingeniería en Software 2026

Aplicación grupal de la materia Ingeniería en Software. Este repositorio contiene la base inicial del proyecto y su documentación de contexto.

## Tecnologías

- Python 3.14.8
- Django 6.1.2
- SQLite para la configuración inicial
- Frontend: pendiente de definición

Python 3.15.0 es la versión estable más reciente, pero Django 6.1 declara soporte oficial hasta Python 3.14. Se fija Python 3.14.8 para mantener una combinación soportada; revisar esta decisión cuando una versión de Django anuncie compatibilidad con Python 3.15. El estado y las decisiones están en [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) y [`docs/DECISIONS.md`](docs/DECISIONS.md).

## Requisitos

- Git
- Python 3.14.8

## Preparar el entorno

Desde la carpeta raíz del repositorio, creá y activá un entorno virtual.

### Windows PowerShell

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación de scripts, podés usar la terminal `cmd.exe`:

```bat
py -3.14 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS y Linux

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Confirmá `python --version` después de activar el entorno. Debe mostrar Python 3.14.8. Instalá Python desde la distribución oficial o el gestor de paquetes aprobado por el equipo.

## Ejecutar el backend

Con el entorno virtual activo:

```bash
cd Backend
python manage.py check
python manage.py migrate
python manage.py runserver
```

Abrí la dirección que muestra Django, normalmente <http://127.0.0.1:8000/>. `runserver` es para desarrollo local. Para detenerlo, presioná `Ctrl+C`; para salir del entorno virtual, ejecutá `deactivate`.

## Estructura

```text
AGENTS.md                 Instrucciones para asistentes de código
Backend/                  Configuración del backend Django
Frontend/                 Espacio reservado; tecnología pendiente
docs/                     Contexto, estado, fuentes y decisiones
requirements.txt          Dependencias Python fijadas
```

Consultá [`docs/INDEX.md`](docs/INDEX.md) antes de comenzar una tarea. No subas entornos virtuales, secretos, archivos `.env` ni bases SQLite locales.
