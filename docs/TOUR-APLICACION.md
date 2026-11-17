# Tour técnico de la aplicación

Este recorrido explica cómo se conectan las interfaces y los datos de un pedido. Los pasos de uso están detallados en el [manual](MANUAL-DE-USO.md); los comandos para iniciar el proyecto y ejecutar la suite están en la [guía](GUIA-EJECUCION-Y-PRUEBAS.md).

## Mapa de módulos

| Aplicación | Responsabilidad | Archivos principales |
|---|---|---|
| `main.homePage` | Enrutamiento de sesiones activas y entrada pública del cliente | `Backend/main/homePage/views.py`, `urls.py`, `Backend/templates/base.html` |
| `main.operario` | Comercios, alta de pedido, panel, detalle y asignación manual | `models.py`, `forms.py`, `views.py`, `urls.py`, `Backend/templates/operario/` |
| `main.repartidor` | Pedido, perfil, estados, historial y evidencia fotográfica | `models.py`, `forms.py`, `views.py`, `urls.py`, `Backend/templates/repartidor/` |
| `main.clienteFinal` | Búsqueda pública e historial de solo lectura | `views.py`, `urls.py`, `Backend/templates/clienteFinal/` |
| `main.users` | Usuario extendido, rol de operario y vehículo | `Backend/main/users/models.py`, `Backend/main/users/migrations/` |
| `config` | Ajustes, URLs globales y entrypoints ASGI/WSGI | `Backend/config/` |

La UI se sirve con plantillas Django. `Frontend/` no contiene una app separada. Bootstrap, iconos y tipografía se cargan desde CDN.

## Recorrido funcional

1. Una persona anónima abre `/` y ve el formulario público de seguimiento. La misma vista está disponible en `/clienteFinal/`; la navegación ofrece accesos separados al login Django del operario y al PIN del repartidor. Una sesión `is_operario` que abre `/` va a `/operario/`; una sesión vinculada a un perfil activo de repartidor va a `/repartidor/`.
2. `PedidoForm` limita el selector a comercios activos y valida dirección, datos del destinatario, tamaño del paquete, vehículo requerido, especificaciones, fecha/hora y clave de idempotencia. Los tres datos agregados para HU33 se capturan como texto libre. La vista repite la validación de comercio dentro de `_crear_pedido`.
3. La transacción crea el pedido `registrado` sin repartidor, persiste los datos capturados, genera un código con `secrets` y registra el evento inicial en `HistorialEstado`. Una restricción de unicidad protege el código y la clave de solicitud; las colisiones de código se reintentan.
4. La confirmación muestra el código y permite copiarlo. El panel permite abrir el pedido y seleccionar un repartidor compatible o dejar la asignación en automático. El servicio de HU 30 verifica disponibilidad, vehículo y ausencia de otro pedido activo; registra la asignación y el evento en el historial.
5. El repartidor autenticado por su PIN ve la asignación en `/repartidor/`, dispone de cinco minutos para responder y luego puede marcar retiro, viaje, entrega o falla, dentro de las transiciones permitidas.
6. Cada cambio de estado guarda un evento. Si se adjunta una foto permitida, la vista valida el contenido, el tipo, el tamaño y la cantidad; la escritura de evento/estado es atómica. El acceso a la evidencia requiere `is_staff`, `is_operario` o ser el repartidor asignado.
7. El cliente busca el código desde `/` o `/clienteFinal/`. La búsqueda dirige al pedido persistido en `/clienteFinal/seguimiento/<codigo>/`. HU 24/38 muestran el estado e historial existentes; la interfaz pública omite contacto, especificaciones, usuarios internos y fotos. La fecha estimada se muestra solo en `en_viaje`.
8. El operario consulta `/operario/pedidos/fallidos/` para ver cada pedido Fallido una sola vez, con datos del evento de falla. La fecha de falla determina el orden ascendente adoptado como propuesta; las fotografías usan el endpoint protegido existente. La confirmación crea una entidad `Devolucion` propia de HU 34 y se muestra junto al evento de falla en la cronología local; no cambia el estado ni la vista pública.

La asignación manual se conserva junto al despacho automático de HU 30. La cercanía contemplada originalmente por HU 22 no se calcula porque el modelo no registra ubicación suficiente; por eso HU 22 no debe considerarse cubierta por completo.

## Recorrido por archivos

- **Panel y detalle del operario:** `Backend/main/operario/urls.py` resuelve a `inicio`, `entregas_fallidas`, `confirmar_devolucion`, `detalle_pedido`, `asignar_repartidor` y las acciones del pedido en `views.py`. `forms.py` filtra perfiles disponibles. `templates/operario/inicio.html` lista el trabajo actual y consulta un endpoint JSON cada 5 segundos; `entregas_fallidas.html` muestra los pedidos fallidos, enlaza fotografías protegidas y presenta la cronología propia de HU 34. `main/operario/models.py` define `Devolucion`, con un registro inmutable por pedido. `detalle_pedido.html` mantiene los datos e historial de HU 33 sin cambios. El mismo detalle ofrece cancelación para estados `registrado` y `asignado` (HU 13), y asignación/reintento según el estado del pedido.
- **Alta:** `PedidoForm` y `ComercioActivoField` viven en `main/operario/forms.py`; `cargar_pedido`, `_crear_pedido` y confirmación están en `views.py`; las plantillas `cargar_pedido.html` y `pedido_registrado.html` construyen el formulario y el resultado.
- **Operación del repartidor:** las URLs de `main/repartidor/urls.py` conectan el PIN, la página, el detalle, la evidencia y los cambios de estado. `ActualizarEstadoForm` en `forms.py` valida fotos. Las vistas limitan las consultas al usuario asociado al perfil y al pedido asignado.
- **Seguimiento:** `main/clienteFinal/views.py` consulta Pedido e HistorialEstado por el código y renderiza `templates/clienteFinal/seguimiento.html`.
- **Navegación global:** `Backend/templates/base.html` presenta enlaces según autenticación y rol. `main.homePage.views.rootHandler` dirige las sesiones activas a su panel y deriva las visitas anónimas a la vista pública de `main.clienteFinal`. `config/urls.py` monta las rutas de las apps y las vistas de autenticación Django.

## Modelo relacional

- `Comercio` mantiene los datos del origen y su indicador `activo`.
- `Pedido` tiene un código único, una clave de idempotencia nullable/única, una relación opcional con comercio, datos del destino, fechas, estado y una relación opcional con `users.User` para el repartidor asignado.
- `Repartidor` enlaza una cuenta con PIN y disponibilidad.
- `HistorialEstado` enlaza pedido y usuario y guarda estado anterior/nuevo, fecha, incidencia y fotografía opcional. La cronología se muestra por fecha y clave primaria.
- `User` extiende `AbstractUser` y mantiene su asociación opcional con un vehículo.

Las migraciones de `Backend/main/repartidor/migrations/` incorporan las relaciones/campos de pedido, el perfil de repartidor y las marcas temporales de asignación/aceptación. La auditoría actual no añadió modelos ni migraciones.

## Recorrido de pruebas

Desde `Backend/`, ejecutá `python manage.py test` para la suite. `main.operario.tests` verifica alta, permisos, panel y asignación; `main.repartidor.tests` cubre PIN, aislamiento, cambios de estado, disponibilidad y fotos; `main.clienteFinal.tests` cubre búsqueda e historial público; `main.homePage.tests` comprueba la entrada pública, las redirecciones por rol, la navegación y el acceso a Django Admin.

## Estado del rediseño de navegación

La entrada anónima `/` presenta el seguimiento público y las opciones de autenticación para operario y repartidor. Las sesiones `is_operario` y las asociadas a un perfil de repartidor activo se dirigen a sus respectivos paneles, evitando que el inicio de sesión vuelva al selector público. La navegación compartida se filtra por rol y es colapsable en pantallas estrechas.

El módulo `/operario/` y sus páginas hijas requieren `is_operario=True`, incluso si la cuenta también tiene `is_staff=False`. Django Admin mantiene el control estándar de Django basado en cuenta activa, `is_staff` y permisos de modelo. Las fotografías enlazadas desde el detalle del operario permiten `is_operario`; las cuentas `is_staff` y el repartidor dueño también conservan el acceso. El repartidor conserva la disponibilidad, aceptación/rechazo, transiciones, fotografías, historial y aislamiento por propietario.

La entrada pública y el panel del operario se inspeccionaron en un navegador local con viewport estrecho; no se inspeccionaron visualmente sesiones de repartidor autenticadas ni escritorio amplio. Las pruebas y límites vigentes están en [`CURRENT_STATE.md`](CURRENT_STATE.md).

## Para seguir aprendiendo

1. Seguí `models.py` para conocer entidades, estados y relaciones.
2. Compará `main/operario/forms.py` con `views.py` para seguir una escritura web y sus validaciones.
3. Leé `main/repartidor/views.py` para ver permisos por usuario, transacciones y almacenamiento de fotos.
4. Compará vistas y plantillas de `clienteFinal` para entender el seguimiento público.
5. Revisá `tests.py` de las apps antes de ampliar cualquier flujo.
6. Leé `DECISIONS.md` y `SOURCE_INDEX.md` para distinguir acuerdos de las historias originales y fuentes.
