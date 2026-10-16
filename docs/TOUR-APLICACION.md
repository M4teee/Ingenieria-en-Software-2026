# Tour de la aplicación

Este documento acompaña la [guía de ejecución y pruebas](GUIA-EJECUCION-Y-PRUEBAS.md). Sigue un pedido desde la carga del operario hasta su consulta pública y el avance del repartidor, y señala qué parte del flujo todavía requiere trabajo.

## Mapa de módulos

| Módulo | Responsabilidad | Archivos de entrada |
|---|---|---|
| `main.operario` | Modelo de comercio, formulario y alta transaccional de pedidos | `Backend/main/operario/models.py`, `forms.py`, `views.py`, `urls.py` |
| `main.repartidor` | Entidades de pedido/historial y avance de estado del repartidor | `Backend/main/repartidor/models.py`, `views.py`, `urls.py` |
| `main.clienteFinal` | Búsqueda pública de un pedido por código y cronología | `Backend/main/clienteFinal/views.py`, `urls.py` |
| `main.homePage` | Redirección de `/` por tipo de cuenta | `Backend/main/homePage/views.py`, `urls.py` |
| `main.users` | Usuario Django extendido y entidad de vehículo | `Backend/main/users/models.py` |
| `config` | Settings, rutas globales y ejecución ASGI/WSGI | `Backend/config/settings.py`, `urls.py`, `wsgi.py`, `asgi.py` |

Las páginas usan plantillas Django en `Backend/templates/`; recursos CSS, imágenes y JavaScript están bajo `Backend/static/`. `Frontend/front` no es una aplicación frontend separada.

## Recorrido funcional

1. El usuario autenticado con `is_staff` abre `/operario/pedidos/nuevo/`. `main.operario.urls` resuelve a `cargar_pedido`.
2. `PedidoForm` valida los campos obligatorios, el UUID de idempotencia, el formato de fecha/hora y la selección de comercio activo. `ComercioActivoField` detecta además un comercio dado de baja para mostrar el mensaje de HU 12.
3. La vista vuelve a comprobar el comercio en `_crear_pedido`, dentro de una transacción. Genera un código con `secrets`, persiste el pedido y crea el evento inicial `Registrado` atribuido al usuario; un error revierte ambos registros. La clave idempotente evita un segundo pedido al reenviar el mismo POST.
4. La redirección posterior al POST abre `pedido_registrado`, que muestra el mensaje de éxito y el código de seguimiento con acción de copiado.
5. HU 24 está en `/clienteFinal/seguimiento/<codigo>/`. `seguimiento` busca el pedido real por código y carga el comercio; la fecha estimada se muestra en estado `en_viaje`. Se muestran campos públicos y estados, no las especificaciones, contacto, usuario ni fotografías.
6. HU 38 se alimenta de `HistorialEstado` persistido. La lista se ordena por fecha y clave primaria. El alta crea `Registrado`; el repartidor añade cambios posteriores al avanzar estado.

La cadena de asignación entre el alta y el repartidor está pendiente: no se halló una pantalla para asignar pedidos. Los pedidos nuevos se crean intencionalmente sin repartidor. Las pruebas de transición verifican reglas del modelo y la vista opera cuando existe una asignación.

## Recorrido por el código

### Alta de operario

- `Backend/main/operario/forms.py` define el formulario y el campo con validación de comercio activo. El formulario convierte la fecha/hora local recibida a una fecha aware siguiendo `USE_TZ` y `TIME_ZONE`.
- `Backend/main/operario/views.py` controla el permiso `is_staff`, realiza la comprobación final del comercio, crea el pedido y su historial dentro de una transacción y maneja colisiones del código.
- `Backend/main/operario/urls.py` expone `/operario/`, `/operario/pedidos/nuevo/` y la confirmación por ID.
- `Backend/templates/operario/cargar_pedido.html` presenta campos, errores y comercios activos. `pedido_registrado.html` muestra el código y el botón de copiar con una alternativa seleccionable si el portapapeles no está disponible.
- `Backend/main/homePage/views.py` dirige usuarios `is_staff` a la pantalla de carga, usuarios comunes a `/repartidor/` y superusuarios al admin.

### Seguimiento e historial

- `Backend/main/clienteFinal/views.py` reemplazó datos de demostración por búsquedas ORM en `Pedido` e `HistorialEstado`.
- `Backend/templates/clienteFinal/seguimiento.html` presenta estado, comercio, hora estimada según el estado y eventos cronológicos.
- `Backend/main/repartidor/views.py` valida las transiciones y registra el evento asociado al usuario; la persistencia del evento y el estado se envuelve en una transacción.
- `Backend/templates/repartidor/` conserva las pantallas del flujo del repartidor. En esta historia no se agregó asignación ni una pantalla para cancelar.

## Recorrido por la base de datos

- `operario_comercio` contiene nombre, dirección, contacto y bandera `activo`.
- `repartidor_pedido` tiene código único, clave de idempotencia única nullable, FK opcional a `Comercio`, datos de destino, fecha estimada, estado y FK opcional al repartidor (`users_user`). La nulabilidad de los campos incorporados permite conservar filas antiguas que no contienen información de HU 12.
- `repartidor_historialestado` relaciona pedido y usuario y guarda estado anterior/nuevo, fecha, incidencia y foto opcional. El orden de presentación es `fecha, pk`.
- `users_user` extiende el usuario Django y mantiene una relación opcional a `users_vehiculo`.
- `Backend/main/repartidor/migrations/0002_pedido_clave_idempotencia_pedido_comercio_and_more.py` agrega los campos, estados y nulabilidad compatibles; `0003_alter_historialestado_options.py` hace estable el orden del historial. No cambia ni borra pedidos existentes.

La base local usada para esta revisión no existía inicialmente y se creó vacía; por eso no se comprobó el contenido de pedidos heredados reales. La guía indica cómo preparar una base de desarrollo sin borrar datos.

## Pruebas por responsabilidad

- HU 12 y formulario: `Backend/main/operario/tests.py` cubre éxito, código único válido, historial atribuido, idempotencia, comercio inactivo, datos inválidos, permisos, carrera de desactivación, colisión de código y rollback.
- Transiciones y flujo existente: `Backend/main/repartidor/tests.py` cubre el avance operativo, la creación de historial, la liberación del repartidor y los nuevos límites de cancelación.
- HU 24/38: `Backend/main/clienteFinal/tests.py` verifica consultas persistidas, 404, solo GET, estados, hora local, orden cronológico y ausencia de datos internos.
- Ejecutá la suite completa desde `Backend/` con `python manage.py test`; los comandos por aplicación y por caso están en la guía.

## Qué cambió con HU 12

Antes, `Pedido` era persistente pero no tenía vínculo con `Comercio`, dirección, especificaciones o fecha estimada; requería repartidor y no incluía `Registrado`. HU 24 y HU 38 usaban pedidos simulados en memoria. No había pantalla operativa para crear pedidos.

Ahora el operario crea pedidos persistidos, el código seguro es consultable por HU 24, y ambas historias de consulta leen el historial compartido. La migración preserva compatibilidad estructural con pedidos previos, los pedidos nuevos nacen sin repartidor y el historial inicial no queda separado del alta. El código del repartidor conserva sus transiciones y ahora guarda estado e historial de forma atómica.

## Para seguir aprendiendo

1. Empezá por `Backend/main/repartidor/models.py` para entender estados, relaciones y reglas de transición.
2. Seguí `Backend/main/operario/forms.py` → `views.py` → `templates/operario/` para aprender el flujo Django de alta.
3. Compará `Backend/main/clienteFinal/views.py` y `templates/clienteFinal/seguimiento.html` para ver consulta ORM y renderizado público.
4. Leé migraciones en orden antes de modificar modelos; Django genera cambios con `python manage.py makemigrations`.
5. Mirá `Backend/main/operario/tests.py` y `Backend/main/repartidor/tests.py` para los patrones de `TestCase`, cliente HTTP y verificación de persistencia.
6. Consultá `docs/DECISIONS.md` y `docs/SOURCE_INDEX.md` para separar acuerdos, requisitos de historias y fuentes académicas.

La interfaz se puede abrir en `http://127.0.0.1:8000/` después de iniciar Django. La guía provee el recorrido manual. La suite inspecciona el HTML, pero todavía no se ha realizado una inspección visual con navegador ni se ha verificado un clic real del portapapeles.
