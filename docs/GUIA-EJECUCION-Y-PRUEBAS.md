# Guía de instalación, ejecución y pruebas

Esta guía prepara el backend Django para desarrollo local y reúne los comandos automatizados. Para los procedimientos desde la interfaz, consultá el [manual de uso](MANUAL-DE-USO.md).

## Requisitos

- Python 3.14 y `pip`; la serie está fijada en `.python-version`.
- Git y una terminal.
- SQLite, incluida con Python. No se requiere un servicio de base de datos ni variables de entorno.
- Dependencias fijadas en `requirements.txt`: Django 6.1.2, asgiref, sqlparse, django-crispy-forms, crispy-bootstrap5 y Pillow.
- Conexión a Internet para descargar dependencias y para cargar Bootstrap, iconos y tipografías desde CDN durante la navegación.

`Backend/config/settings.py` usa `DEBUG=True`, una clave de desarrollo y SQLite. Esta configuración es exclusivamente local y no debe utilizarse en producción.

## Preparación desde cero

Cloná el repositorio y ubicáte en su raíz:

```sh
git clone <URL-del-repositorio>
cd Ingenieria-en-Software-2026
```

En macOS o Linux, creá el entorno e instalá las versiones fijadas:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd Backend
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

En Fish, activá el mismo entorno con `source .venv/bin/activate.fish` antes de entrar a `Backend/`. En Windows PowerShell:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd Backend
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

`createsuperuser` solicita los datos de acceso en forma interactiva; el repositorio no contiene cuentas de prueba. `migrate` prepara `Backend/db.sqlite3`. No borres esa base para resolver errores: podría contener datos locales que deban conservarse. El comando `runserver` imprime la dirección local, normalmente `http://127.0.0.1:8000/`. Detenelo con `Ctrl+C`.

Los pasos de instalación se basan en la configuración real. En esta revisión, la instalación de los paquetes fijados se completó en el entorno virtual local. Una instalación limpia en otra computadora depende del acceso a PyPI.

## Pruebas y comprobaciones

Con el entorno virtual activo y desde `Backend/`:

```sh
python manage.py test
python manage.py test main.operario
python manage.py test main.repartidor
python manage.py test main.clienteFinal
python manage.py test main.operario.tests.PanelOperarioTests
python manage.py test main.repartidor.tests.ActualizarEstadoTests.test_fallido_registra_incidencia
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python -m pip check
```

La primera línea ejecuta la suite completa; las siguientes permiten acotar por aplicación, clase o caso. `check` revisa la configuración Django; `makemigrations --check --dry-run` informa si los modelos requieren una migración nueva; `migrate --check` detecta migraciones pendientes; `pip check` revisa dependencias instaladas incompatibles. No hay una herramienta de lint o formato declarada.

Desde la raíz, comprobá enlaces y rutas relativas de documentación con:

```sh
python3 scripts/check_docs.py .
git diff --check
```

### Resultados de esta revisión

Con Python 3.14.8 y las dependencias de `requirements.txt`, desde `Backend/` se ejecutaron en la revisión del rediseño: `../.venv/bin/python manage.py check` (aprobado) y `../.venv/bin/python manage.py test` (70 pruebas aprobadas). Desde la raíz, `python3 scripts/check_docs.py .` verificó 42 enlaces y `git diff --check` pasó. La revisión previa había aprobado además `makemigrations --check --dry-run`, `migrate --check` y `pip check`. La suite usa una base temporal y no borra la base local.

La aplicación se abrió en un navegador local y se inspeccionaron visualmente la entrada pública y el panel de operario en un viewport estrecho, sin escribir datos. No se realizó una inspección visual autenticada del módulo del repartidor ni de escritorio amplio. El Django Test Client comprobó el acceso a la raíz, las redirecciones por rol, la navegación sin enlaces cruzados, el acceso protegido a Django Admin y las pruebas existentes de propiedad de pedidos y operaciones. Windows no se probó.

### Escenarios de navegación y permisos

- Persona anónima: `/` muestra la búsqueda pública y los accesos diferenciados a `/login/?next=/operario/` y `/repartidor/login-pin/`.
- Cuenta activa `is_operario`: el login redirige al panel `/operario/`; abrir `/` desde una sesión activa también lleva al panel. Tener `is_staff` sin `is_operario` no concede acceso al módulo.
- Cuenta con perfil activo de repartidor: el PIN inicia sesión y `/` lleva a `/repartidor/`.
- `is_operario` y `is_staff` son independientes: `is_operario` permite el módulo de operario y `is_staff` permite entrar a Django Admin (sujeto a permisos de modelo). Ninguno exige ser superusuario.
- La navegación pública no muestra herramientas operativas; la del repartidor no ofrece seguimiento ni acciones de operario; el panel de operario mantiene una sola acción principal para cargar pedidos.

## Limitaciones conocidas

- No hay configuración de CI ni comprobaciones estáticas adicionales declaradas.
- Los estilos e iconos se cargan desde CDN; sin red, el contenido sigue disponible pero puede presentarse sin esos recursos.
- No se ensayó la migración sobre una base poblada con datos heredados reales.
- No se validó el despliegue en producción, el almacenamiento remoto de fotografías ni el comportamiento en Windows.
- La asignación desde el panel del operario es un puente provisional manual. Las HU 22 y 30, que piden asignación automática, siguen sin implementar y no se consideran completas. La decisión está descrita en [`DECISIONS.md`](DECISIONS.md).

## Errores frecuentes

- **No se puede activar el entorno en Fish:** usá `source .venv/bin/activate.fish`, no el script de Bash/Zsh `activate`.
- **No se encuentra Django:** confirmá que el entorno `.venv` esté activo y ejecutá `python -m pip install -r requirements.txt` desde la raíz.
- **Migraciones pendientes:** desde `Backend/`, revisá `showmigrations` y ejecutá `python manage.py migrate`. No recrees ni borres SQLite.
- **Carga denegada:** el usuario debe tener `is_operario=True` y haber iniciado sesión.
- **Permiso operativo tras migrar:** la migración `users.0004_user_is_operario` conserva los accesos de las cuentas que ya tenían `is_staff=True`; nuevas cuentas deben recibir `is_operario=True` para abrir `/operario/`.
- **No aparece un comercio o repartidor:** comprobá en Django Admin que el comercio esté activo y que el perfil del repartidor esté activo y disponible, y que no tenga otro pedido activo.
- **Prueba fallida:** ejecutá el caso por separado y revisá el traceback antes de cambiar datos locales.
