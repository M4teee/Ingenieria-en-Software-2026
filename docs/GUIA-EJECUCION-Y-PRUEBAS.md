# Guía de instalación, ejecución y pruebas

Esta guía prepara el backend Django para desarrollo local y reúne los comandos automatizados. Para los procedimientos desde la interfaz, consultá el [manual de uso](MANUAL-DE-USO.md).

## Requisitos

- Python 3.14 y `pip`; la serie está fijada en `.python-version`.
- Git y una terminal.
- SQLite, incluida con Python. No se requiere un servicio de base de datos ni variables de entorno.
- Dependencias fijadas en `requirements.txt`: Django 6.1.2, asgiref, sqlparse, django-crispy-forms, crispy-bootstrap5, Pillow, `dj-database-url`, `python-dotenv` y Psycopg 3 con su binario.
- Conexión a Internet para descargar dependencias y para cargar Bootstrap, iconos y tipografías desde CDN durante la navegación.

`Backend/config/settings.py` usa `DEBUG=True` y una clave de desarrollo. Sin una variable `DATABASE_URL` no vacía, usa `Backend/db.sqlite3`; con una URL `postgres://` o `postgresql://`, usa PostgreSQL (incluido Neon). Esta configuración es de desarrollo y no debe utilizarse en producción.

La suite automatizada usa `Backend/config/settings_test.py`, que fuerza SQLite en memoria aunque exista un `DATABASE_URL` local. No hace falta configurar Neon ni copiar credenciales para ejecutar pruebas.

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

## Elegir y ejecutar la base de datos

La aplicación carga `.env` desde la raíz del repositorio (`Backend/config/settings.py`). Una variable `DATABASE_URL` ya exportada en la terminal tiene precedencia sobre `.env`. El valor vacío selecciona SQLite. Un valor no vacío debe comenzar con `postgres://` o `postgresql://`; un esquema incorrecto produce un error de configuración, no cambia silenciosamente a SQLite.

### A. SQLite local

1. Asegurate de que `DATABASE_URL` esté vacía o no esté definida. Si tenés una URL de Neon en `.env`, en macOS/Linux iniciá los comandos así: `DATABASE_URL='' python manage.py ...`. En PowerShell: `$env:DATABASE_URL = ''`.
2. Desde `Backend/`, prepará el esquema y comprobá la configuración:

   ```sh
   python manage.py check
   python manage.py migrate
   python manage.py showmigrations
   python manage.py runserver
   ```

3. Abrí `http://127.0.0.1:8000/`. La base predeterminada es `Backend/db.sqlite3`; `migrate` la crea si no existe. Si ya existe, no la borres: conservá una copia antes de aplicar migraciones.

Para confirmar el motor seleccionado sin conectar a un servicio remoto, ejecutá desde `Backend/`:

```sh
DATABASE_URL='' python manage.py shell -c 'from django.conf import settings; print(settings.DATABASES["default"]["ENGINE"])'
```

Debe imprimir `django.db.backends.sqlite3`.

### B. PostgreSQL en Neon

1. Creá o seleccioná en Neon una base de desarrollo del proyecto. En el panel de Neon, copiá el connection string de PostgreSQL que corresponda a esa base. La cadena contiene credenciales; no la pegues en Git, tickets, capturas ni mensajes del equipo.
2. Creá `.env` en la raíz del repositorio (está ignorado por Git) y definí la variable que lee la configuración:

   ```dotenv
   DATABASE_URL=postgresql://USUARIO:CLAVE@HOST/BASE?sslmode=require
   ```

   Reemplazá el ejemplo por la URL copiada de Neon, conservando sus parámetros. No agregues comillas si la cadena no las requiere. También podés exportar `DATABASE_URL` en la terminal; ese valor prevalece sobre `.env`.
3. Confirmá que se seleccionó y que la conexión funciona. Desde `Backend/`:

   ```sh
   python manage.py check
   python manage.py shell -c 'from django.db import connection; connection.ensure_connection(); print(connection.vendor, connection.settings_dict["HOST"])'
   ```

   La segunda orden abre una conexión y debe mostrar `postgresql` y el host configurado. No imprime usuario ni contraseña.
4. Aplicá el esquema a la base Neon de desarrollo y revisá el resultado:

   ```sh
   python manage.py migrate
   python manage.py showmigrations
   python manage.py runserver
   ```

   `migrate` escribe cambios de esquema en la base elegida. Verificá antes que la URL apunte a una rama/base de desarrollo autorizada; no ejecutes estas órdenes contra producción.
5. Abrí `http://127.0.0.1:8000/` y recorré una pantalla que lea datos. La comprobación de conexión más explícita sigue siendo la orden con `connection.ensure_connection()`; `check` por sí solo no prueba conectividad.

La selección del motor se basa únicamente en `DATABASE_URL`. El modo PostgreSQL se configura con Psycopg, comprobaciones de salud y un pool local de hasta cinco conexiones. No hay variables separadas para host, usuario o clave. Para volver a SQLite, vaciá `DATABASE_URL` en la terminal; si existe `.env`, la variable vacía exportada prevalece mientras dure esa sesión.

Errores frecuentes con Neon:

- `ImproperlyConfigured ... DATABASE_URL`: usá el connection string de PostgreSQL (`postgres://` o `postgresql://`) o vaciá la variable para SQLite.
- Error de resolución, timeout o TLS: revisá que la URL se haya copiado completa, que la base esté activa y que la red permita conectarse al host/puerto indicados por Neon.
- `password authentication failed`: generá/copialá de nuevo la cadena desde Neon y actualizá `.env`; no publiques la clave.
- `relation ... does not exist`: aplicá `python manage.py migrate` en esa base de desarrollo.
- Las pruebas automáticas usan `settings_test` y SQLite en memoria; no prueban Neon ni leen `.env` para seleccionar la base.

En la auditoría del 2026-11-19 no había `.env` ni credenciales de Neon en el entorno. Por eso la ruta de Neon quedó documentada a partir del código, pero su conexión y sus migraciones no se ejecutaron.

## Pruebas y comprobaciones

Con el entorno virtual activo y desde `Backend/`:

```sh
python manage.py test --settings=config.settings_test
python manage.py test main.operario --settings=config.settings_test
python manage.py test main.repartidor --settings=config.settings_test
python manage.py test main.clienteFinal --settings=config.settings_test
python manage.py test main.operario.tests.PanelOperarioTests --settings=config.settings_test
python manage.py test main.repartidor.tests.ActualizarEstadoTests.test_fallido_registra_incidencia --settings=config.settings_test
python manage.py check --settings=config.settings_test
python manage.py makemigrations --check --dry-run
python -m pip check
```

La primera línea ejecuta la suite completa; las siguientes permiten acotar por aplicación, clase o caso. El módulo `settings_test` mantiene la base de pruebas aislada en SQLite en memoria y evita conectarse por accidente a Neon. `check` revisa la configuración Django; `makemigrations --check --dry-run` informa si los modelos requieren una migración nueva; `pip check` revisa dependencias instaladas incompatibles. Para comprobar migraciones pendientes en una base de desarrollo configurada, ejecutá `python manage.py migrate --check` con la configuración apropiada. No hay una herramienta de lint o formato declarada.

Desde la raíz, comprobá enlaces y rutas relativas de documentación con:

```sh
python3 scripts/check_docs.py .
git diff --check
```

### Resultados de la auditoría pre-demo del 2026-11-19

Con Django 6.1.2 y las dependencias fijadas instaladas en un entorno temporal con Python 3.13.16, se ejecutó desde `Backend/` `/tmp/sgr-audit-venv/bin/python manage.py test --settings=config.settings_test`: 182 pruebas aprobadas, 0 fallos y 0 errores. La configuración declarada del proyecto requiere Python 3.14; la ejecución con 3.13 sirve como comprobación en este host, no como verificación del intérprete objetivo. También pasaron `check`, `makemigrations --check --dry-run` y `pip check`; la revisión final de `scripts/check_docs.py .` verificó 48 enlaces. La suite usa SQLite en memoria y no conecta a Neon ni modifica la SQLite existente.

Prueba manual en navegador local, con base SQLite descartable separada de `Backend/db.sqlite3` y viewport 663×711: portada pública; login, panel y detalle de operario; lista/filtro de comercios; lista y diálogo de regeneración de PIN; login del repartidor, aceptación y ciclo de estados hasta Entregado; seguimiento público. El seguimiento mostró únicamente el estado, el comercio y la cronología, sin datos internos. No se inspeccionó escritorio ancho ni todas las pantallas; Windows no se probó.

### Escenarios de navegación y permisos

- Persona anónima: `/` muestra la búsqueda pública y los accesos diferenciados a `/login/?next=/operario/` y `/repartidor/login-pin/`.
- Cuenta activa `is_operario`: el login redirige al panel `/operario/`; abrir `/` desde una sesión activa también lleva al panel. Tener `is_staff` sin `is_operario` no concede acceso al módulo.
- Cuenta con perfil activo de repartidor: el PIN inicia sesión y `/` lleva a `/repartidor/`.
- `is_operario` y `is_staff` son independientes: `is_operario` permite el módulo de operario y `is_staff` permite entrar a Django Admin (sujeto a permisos de modelo). Ninguno exige ser superusuario.
- La navegación pública no muestra herramientas operativas; la del repartidor no ofrece seguimiento ni acciones de operario; el panel de operario mantiene una sola acción principal para cargar pedidos.

## Limitaciones conocidas

- No hay configuración de CI, lint ni comprobaciones estáticas adicionales declaradas.
- Los estilos e iconos se cargan desde CDN; sin red, el contenido sigue disponible pero puede presentarse sin esos recursos.
- No se ensayó la migración sobre una base poblada con datos heredados reales.
- No se validó el despliegue en producción, el almacenamiento remoto de fotografías ni el comportamiento en Windows.
- La HU 18 no envía una notificación activa al operario ante un rechazo; la expiración se procesa al consultar o responder, no mediante una tarea en segundo plano.
- El login por PIN no tiene limitación de intentos. La app no se debe exponer a Internet en su configuración actual.
- La HU 34 tiene una sola confirmación de devolución por pedido; falta validar con el equipo si el proceso permite varias recepciones. La dirección del orden por fecha también queda abierta en la fuente.
- Las HUs 22, 30 y 41 tienen responsabilidades diferentes según el export del 19/11/2026: visualización de asignación, alerta y despacho automático FIFO. No se calcula cercanía geográfica porque las HUs 41/42 del snapshot no la exigen y el modelo no registra ubicación suficiente.
- La revisión visual fue parcial: faltan formularios de alta, historial completo, pantalla de entregas fallidas y viewport de escritorio amplio.

## Errores frecuentes

- **No se puede activar el entorno en Fish:** usá `source .venv/bin/activate.fish`, no el script de Bash/Zsh `activate`.
- **No se encuentra Django:** confirmá que el entorno `.venv` esté activo y ejecutá `python -m pip install -r requirements.txt` desde la raíz.
- **Migraciones pendientes:** desde `Backend/`, revisá `showmigrations` y ejecutá `python manage.py migrate`. No recrees ni borres SQLite.
- **Carga denegada:** el usuario debe tener `is_operario=True` y haber iniciado sesión.
- **Permiso operativo tras migrar:** la migración `users.0004_user_is_operario` conserva los accesos de las cuentas que ya tenían `is_staff=True`; nuevas cuentas deben recibir `is_operario=True` para abrir `/operario/`.
- **No aparece un comercio o repartidor:** comprobá en Django Admin que el comercio esté activo y que el perfil del repartidor esté activo y disponible, y que no tenga otro pedido activo.
- **Prueba fallida:** ejecutá el caso por separado y revisá el traceback antes de cambiar datos locales.
