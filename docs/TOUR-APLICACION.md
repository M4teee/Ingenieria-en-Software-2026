# Tour técnico de la aplicación

Este recorrido explica cómo se conectan las interfaces y los datos de un pedido. Los pasos de uso están detallados en el [manual](MANUAL-DE-USO.md); los comandos para iniciar el proyecto y ejecutar la suite están en la [guía](GUIA-EJECUCION-Y-PRUEBAS.md).

## Mapa de módulos

| Aplicación | Responsabilidad | Archivos principales |
|---|---|---|
| `main.homePage` | Página de acceso y enrutamiento según la cuenta | `Backend/main/homePage/views.py`, `urls.py`, `Backend/templates/home.html` |
| `main.operario` | Comercios, alta de pedido, panel, detalle y asignación manual | `models.py`, `forms.py`, `views.py`, `urls.py`, `Backend/templates/operario/` |
| `main.repartidor` | Pedido, perfil, estados, historial y evidencia fotográfica | `models.py`, `forms.py`, `views.py`, `urls.py`, `Backend/templates/repartidor/` |
| `main.clienteFinal` | Búsqueda pública e historial de solo lectura | `views.py`, `urls.py`, `Backend/templates/clienteFinal/` |
| `main.users` | Usuario extendido y vehículo | `Backend/main/users/models.py` |
| `config` | Ajustes, URLs globales y entrypoints ASGI/WSGI | `Backend/config/` |

La UI se sirve con plantillas Django. `Frontend/` no contiene una app separada. Bootstrap, iconos y tipografía se cargan desde CDN.

## Recorrido funcional

1. El usuario autenticado con `is_staff` llega desde `/` al panel `/operario/`. Desde ahí abre `/operario/pedidos/nuevo/`.
2. `PedidoForm` limita el selector a comercios activos y valida campos, fecha/hora y clave de idempotencia. La vista repite la validación de comercio dentro de `_crear_pedido`.
3. La transacción crea el pedido `registrado` sin repartidor, genera un código con `secrets` y registra el evento inicial en `HistorialEstado`. Una restricción de unicidad protege el código y la clave de solicitud; las colisiones de código se reintentan.
4. La confirmación muestra el código y permite copiarlo. El panel permite abrir el pedido y seleccionar manualmente un repartidor disponible; el servidor verifica otra vez que siga disponible y registra el cambio a `asignado` y su historial.
5. El repartidor autenticado por su PIN ve la asignación en `/repartidor/`, dispone de cinco minutos para responder y luego puede marcar retiro, viaje, entrega o falla, dentro de las transiciones permitidas.
6. Cada cambio de estado guarda un evento. Si se adjunta una foto permitida, la vista valida el contenido, el tipo, el tamaño y la cantidad; la escritura de evento/estado es atómica. El acceso a la evidencia requiere ser staff o el repartidor asignado.
7. El cliente busca el código desde `/clienteFinal/`. La búsqueda dirige al pedido persistido en `/clienteFinal/seguimiento/<codigo>/`. HU 24/38 muestran el estado e historial existentes; la interfaz pública omite contacto, especificaciones, usuarios internos y fotos. La fecha estimada se muestra solo en `en_viaje`.

La asignación manual es un puente provisional elegido para la aplicación web. Las HU 22 y 30 siguen sin implementar y no se consideran completas: el flujo no realiza asignación automática ni cálculo de cercanía.

## Recorrido por archivos

- **Panel y detalle del operario:** `Backend/main/operario/urls.py` resuelve a `inicio`, `detalle_pedido` y `asignar_repartidor` en `views.py`. `forms.py` filtra perfiles disponibles. `templates/operario/inicio.html` lista el trabajo actual y consulta un endpoint JSON cada 15 segundos; `detalle_pedido.html` muestra datos, historial y asignación.
- **Alta:** `PedidoForm` y `ComercioActivoField` viven en `main/operario/forms.py`; `cargar_pedido`, `_crear_pedido` y confirmación están en `views.py`; las plantillas `cargar_pedido.html` y `pedido_registrado.html` construyen el formulario y el resultado.
- **Operación del repartidor:** las URLs de `main/repartidor/urls.py` conectan el PIN, la página, el detalle, la evidencia y los cambios de estado. `ActualizarEstadoForm` en `forms.py` valida fotos. Las vistas limitan las consultas al usuario asociado al perfil y al pedido asignado.
- **Seguimiento:** `main/clienteFinal/views.py` consulta Pedido e HistorialEstado por el código y renderiza `templates/clienteFinal/seguimiento.html`.
- **Navegación global:** `Backend/templates/base.html` presenta enlaces según autenticación y rol. `config/urls.py` monta las rutas de las apps.

## Modelo relacional

- `Comercio` mantiene los datos del origen y su indicador `activo`.
- `Pedido` tiene un código único, una clave de idempotencia nullable/única, una relación opcional con comercio, datos del destino, fechas, estado y una relación opcional con `users.User` para el repartidor asignado.
- `Repartidor` enlaza una cuenta con PIN y disponibilidad.
- `HistorialEstado` enlaza pedido y usuario y guarda estado anterior/nuevo, fecha, incidencia y fotografía opcional. La cronología se muestra por fecha y clave primaria.
- `User` extiende `AbstractUser` y mantiene su asociación opcional con un vehículo.

Las migraciones de `Backend/main/repartidor/migrations/` incorporan las relaciones/campos de pedido, el perfil de repartidor y las marcas temporales de asignación/aceptación. La auditoría actual no añadió modelos ni migraciones.

## Recorrido de pruebas

Desde `Backend/`, ejecutá `python manage.py test` para las 64 pruebas. `main.operario.tests` verifica alta, permisos, panel y asignación; `main.repartidor.tests` cubre PIN, aislamiento, cambios de estado, disponibilidad y fotos; `main.clienteFinal.tests` cubre búsqueda e historial público; `main.homePage.tests` comprueba el enrutamiento inicial. La guía tiene comandos por aplicación y comprobaciones de configuración y migraciones.

## Qué cambió en esta revisión

La aplicación tenía pedidos y varias vistas, pero la navegación no conectaba con claridad el inicio, el panel del operario y el público; faltaba un enlace claro desde el panel hacia pedidos y no había una UI del operario para la asignación que el equipo eligió. Ahora hay panel, detalles, asignación manual y acceso directo desde menús por rol. El repartidor conserva las transiciones existentes y gana un detalle/historial por pedido, protección de evidencia y validación de archivos. La búsqueda pública ofrece una entrada accesible y conserva consultas persistidas.

La navegación y pantallas principales se inspeccionaron en el navegador local. La suite automatizada pasó; no se hizo un recorrido visual autenticado completo con creación de pedido, asignación y carga de fotos. Ver los resultados vigentes en [`CURRENT_STATE.md`](CURRENT_STATE.md).

## Para seguir aprendiendo

1. Seguí `models.py` para conocer entidades, estados y relaciones.
2. Compará `main/operario/forms.py` con `views.py` para seguir una escritura web y sus validaciones.
3. Leé `main/repartidor/views.py` para ver permisos por usuario, transacciones y almacenamiento de fotos.
4. Compará vistas y plantillas de `clienteFinal` para entender el seguimiento público.
5. Revisá `tests.py` de las apps antes de ampliar cualquier flujo.
6. Leé `DECISIONS.md` y `SOURCE_INDEX.md` para distinguir acuerdos de las historias originales y fuentes.
