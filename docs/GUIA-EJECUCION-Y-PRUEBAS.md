# Guía de ejecución y pruebas

Guía para preparar y recorrer el backend completo en desarrollo. Los comandos y resultados de verificación citados corresponden a macOS, Python 3.14.8 y Django 6.1.2 en la rama `feature/hu-12-cargar-pedido`; Windows no se probó.

## Requisitos previos

- Python 3.14 (el archivo `.python-version` indica la serie `3.14`; esta revisión instaló Python 3.14.8) y `pip` incluido con Python.
- Git y una terminal. No se requiere Node.js ni una base externa.
- Dependencias fijadas en `requirements.txt`: Django, asgiref, sqlparse, django-crispy-forms, crispy-bootstrap5 y Pillow.
- SQLite está configurado en `Backend/config/settings.py`; no se requieren variables de entorno ni servicios externos para la configuración local.
- La configuración Django usa `DEBUG=True`, una clave de desarrollo y `ALLOWED_HOSTS=[]`. Es solo para desarrollo. Las plantillas cargan Bootstrap, iconos y tipografías desde CDN; para ver esos estilos se necesita conexión a Internet.

## Preparación desde cero

Desde una copia del repositorio:

```sh
git clone <URL-del-repositorio>
cd Ingenieria-en-Software-2026
```

En macOS o Linux:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cd Backend
python manage.py check
python manage.py migrate
```

En Windows PowerShell, usando una instalación de Python 3.14:

```powershell
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cd Backend
python manage.py check
python manage.py migrate
```

La instalación de paquetes requiere acceso a PyPI. En esta revisión se completó con las versiones exactas de `requirements.txt`; al primer intento la red del entorno aislado bloqueó DNS y luego se habilitó la instalación. `pip check` no encontró requisitos rotos.

`migrate` crea o actualiza `Backend/db.sqlite3`, que está excluido de Git. No borres esa base si contiene trabajo que querés conservar. Para una base vacía, creá un administrador:

```sh
python manage.py createsuperuser
```

El comando solicita usuario, correo y contraseña en forma interactiva; no hay credenciales de ejemplo. Iniciá el servidor:

```sh
python manage.py runserver
```

Abrí `http://127.0.0.1:8000/`. Para apagarlo, usá `Ctrl+C`; para salir del entorno virtual, `deactivate`.

## Ejecutar pruebas y comprobaciones

Ejecutá desde `Backend/` con el entorno virtual activo:

```sh
python manage.py test
```

Ejecuta toda la suite de las aplicaciones instaladas. Para una aplicación o clase concreta:

```sh
python manage.py test main.operario
python manage.py test main.repartidor
python manage.py test main.clienteFinal
python manage.py test main.operario.tests.CargarPedidoTests
```

Para un caso individual, agregá el nombre del método, por ejemplo `main.operario.tests.CargarPedidoTests.test_alta_crea_pedido_historial_y_muestra_codigo`.

Comprobaciones de configuración, migraciones y dependencias:

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python -m pip check
```

`check` analiza configuración Django; `makemigrations --check --dry-run` detecta cambios de modelos sin migración; `migrate --check` falla si hay migraciones sin aplicar; `pip check` informa paquetes incompatibles. El proyecto no declara una herramienta de lint o formato.

## Recorrido manual de las funcionalidades

Las acciones de alta, consulta pública y avance del repartidor modifican SQLite. Usá datos de desarrollo. No ejecutes `flush`, no borres `db.sqlite3` y no uses información real.

1. Iniciá sesión como superusuario en `http://127.0.0.1:8000/admin/`.
2. En **Comercios**, creá un comercio activo con nombre, dirección y contacto ficticios.
3. En **Usuarios**, creá un usuario de operario y marcá `is_staff`. Cerrá la sesión administrativa y accedé con ese usuario.
4. Abrí `/operario/pedidos/nuevo/`. El selector debe listar solo comercios activos. Intentá enviar el formulario vacío y comprobá que no se cree un pedido y se indiquen los campos obligatorios.
5. Completá comercio, dirección, especificaciones y fecha/hora estimadas, y presioná **Registrar Pedido**. La confirmación muestra “Pedido registrado con éxito”, el código, estado `Registrado` y botón **Copiar código**. En `localhost`, el navegador puede ofrecer la API del portapapeles; si la bloquea, la pantalla selecciona el código para copiarlo manualmente.
6. Abrí `/clienteFinal/seguimiento/<codigo>/` con el código de confirmación. La consulta pública muestra el estado, comercio e historial inicial `Registrado`. En ese estado todavía no muestra la estimación: el diseño existente solo la enseña cuando el pedido está `en_viaje`.
7. Reenviar el mismo formulario con la misma clave de solicitud no duplica el pedido; recargar la confirmación tampoco lo crea de nuevo. Probá un código inexistente: la consulta debe responder 404.
8. Para probar el rechazo por comercio inactivo, volvé al admin, desactivá el comercio y enviá un POST con ese comercio seleccionado. El servidor debe rechazarlo con “El comercio seleccionado se encuentra inhabilitado para nuevos pedidos”. El formulario impide elegirlo normalmente, por lo que esta prueba negativa requiere forjar el POST desde las herramientas del navegador o un cliente HTTP autenticado; no reutilices formularios de producción.
9. Cerrá sesión y comprobá permisos: un usuario anónimo que abre la carga va a `/login/`; un usuario autenticado sin `is_staff` recibe 403. Las pruebas automatizadas cubren ambos casos y la vista de confirmación.

### Avance del repartidor

No hay una pantalla de asignación de pedidos. Para explorar la interfaz existente, primero creá con el admin un usuario de repartidor (sin `is_staff`) y un pedido de prueba asignado, o prepará el pedido con el shell de Django. El siguiente ejemplo inserta un pedido ficticio asignado al usuario cuyo nombre y comercio adaptes; agrega la historia inicial y la asignación en el mismo bloque:

```sh
python manage.py shell
```

```python
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from main.operario.models import Comercio
from main.repartidor.models import HistorialEstado, Pedido
from main.users.models import User

repartidor = User.objects.get(username="usuario_repartidor_de_prueba")
comercio = Comercio.objects.get(nombre="Comercio ficticio")
codigo = Pedido.generar_codigo()
while Pedido.objects.filter(codigo=codigo).exists():
    codigo = Pedido.generar_codigo()

with transaction.atomic():
    pedido = Pedido.objects.create(
        codigo=codigo,
        comercio=comercio,
        direccion_destino="Dirección ficticia 123",
        especificaciones_traslado="Pedido de prueba",
        fecha_hora_estimada_entrega=timezone.now() + timedelta(hours=3),
        estado="asignado",
        repartidor=repartidor,
    )
    HistorialEstado.objects.create(
        pedido=pedido,
        estado_nuevo="registrado",
        usuario=repartidor,
    )
    HistorialEstado.objects.create(
        pedido=pedido,
        estado_anterior="registrado",
        estado_nuevo="asignado",
        usuario=repartidor,
    )
print(pedido.codigo)
```

Salí del shell con `exit()`, iniciá sesión como ese repartidor y abrí `/repartidor/`. Avanzá `Asignado → Retirado → En viaje`; después consultá el código impreso en la URL pública. Para el recorrido de cierre, avanzá de `En viaje` a `Entregado` o `Fallido`. Cada transición crea un evento persistido. Cancelación es válida antes del retiro, pero todavía no hay interfaz para operar esa transición.

### Datos y limpieza

Los pasos de navegador crean usuarios, comercios, pedidos e historial en `Backend/db.sqlite3`. Conservalos si los necesitás. Para repetir pruebas sin perder otros registros, usá nombres y pedidos nuevos. La suite `manage.py test` usa una base temporal separada y la elimina al finalizar. No hay un comando de limpieza de fixtures documentado porque podría borrar datos útiles.

## Diagnóstico de errores frecuentes

- **Falta Django u otra dependencia:** activá `.venv` e instalá `python -m pip install -r requirements.txt`; luego `python -m pip check`. En esta revisión se verificó que las seis dependencias fijadas se instalaron y resolvieron.
- **Error de DNS al instalar:** verificá conectividad a PyPI o usá el entorno de paquetes institucional. Durante esta tarea el primer intento fue bloqueado por la red aislada; la instalación posterior terminó correctamente.
- **Migraciones pendientes:** ejecutá `python manage.py migrate`; revisá `showmigrations` si necesitás identificar cuáles faltan. No elimines la base como método de reparación.
- **No existe la base/tablas:** ejecutá `python manage.py migrate` desde `Backend/`.
- **No aparece un comercio en el selector:** verificá `activo=True` en el admin. Los comercios inactivos se excluyen deliberadamente y el servidor vuelve a validarlo.
- **403 en carga:** iniciá sesión con un usuario que tenga `is_staff=True`. Ser usuario autenticado no alcanza.
- **Error en una prueba:** volvé a ejecutar el caso específico con el identificador de la sección anterior y leé el traceback; la salida señala archivo, línea y aserción que falló.
- **Sin estilos o iconos:** la plantilla obtiene Bootstrap y recursos gráficos desde CDN; comprobá conectividad. El HTML del sistema se sirve localmente.
- **No podés asignar un pedido desde una pantalla:** esa interfaz todavía no existe; el flujo de repartidor solo opera pedidos ya asignados.

## Estado de validación de esta guía

Se verificaron en la instalación local: `check`, `makemigrations --check --dry-run`, `migrate --check`, `pip check` y las 30 pruebas de la suite completa. También se recorrió en navegador local el login de operario, formulario, alta, confirmación con código, copiado real al portapapeles y consulta pública. Se retiraron de SQLite el usuario, comercio y pedido ficticios usados para esa comprobación; la base mantiene aplicadas las migraciones y queda sin esos fixtures. La instalación limpia se ejecutó en un entorno virtual nuevo; Windows queda pendiente de validación.
