# Decisiones y temas abiertos

Este registro conserva el estado que ya estaba anotado y separa los hechos del repositorio de los acuerdos del equipo. No atribuir una decisión a una persona si la fuente no lo hace.

## Decisiones registradas

| Fecha registrada | Tema | Estado |
|---|---|---|
| 2026-10-11 | Python 3.14.8 para el entorno de trabajo | Registrada como acordada en la documentación previa. `.python-version` especifica la serie `3.14`, no el parche. |
| 2026-10-11 | Django 6.1.2 | Registrada como versión elegida para el backend. |
| 2026-10-15 | HU 12 — datos del pedido | Aprobado para la implementación: especificaciones en texto libre; ETA como fecha y hora con la zona horaria Django; sin repartidor al crear; estado inicial `registrado`; evento inicial atribuido al operario. |
| 2026-10-15 | HU 12, HU 24 y HU 38 — flujo | Aprobado para la implementación: formulario web propio bajo `/operario/` para usuarios autenticados `is_staff`; código seguro, alfanumérico y único; pedidos persistidos consultables por su código y con historial persistido. La creación del pedido y su evento inicial se realiza de forma atómica. |
| 2026-10-16 | Puente provisional de asignación | Aprobado para esta etapa: el operario elige desde la web un perfil de repartidor activo y disponible. Se implementó asignación manual para conectar el registro con el módulo web. La asignación automática de HU 22/30 queda para una etapa posterior; esas historias no se consideran implementadas ni completas. |
| 2026-10-16 | Rediseño de navegación SGR | Implementado según la consigna de esta tarea: `/` ofrece la consulta pública; las sesiones activas `is_staff` y de repartidor con perfil activo se dirigen a su panel. La navegación presenta acciones por rol. Django Admin conserva su autorización estándar de usuario activo con `is_staff` y permisos de modelo. No se agregaron permisos ni roles nuevos. |
| 2026-10-26 | Autorización del módulo de operario | Aprobado por el usuario: el acceso a todas las vistas de `/operario/` se determina por `User.is_operario`, separado de `is_staff`, que conserva su función para Django Admin. La migración inicial copia los valores existentes de `is_staff` para no quitar acceso al desplegar el cambio. |
| 2026-11-04 | HU 29 — Deshabilitar repartidor | Aprobado para la implementación: se reutiliza `User.is_active` como la bandera de borrado lógico del repartidor (no se agrega un campo `activo` nuevo al modelo `Repartidor`), porque el código ya usaba ese campo para cortar el login por PIN (`login_pin`) y para excluir al repartidor de la asignación manual (`asignar_repartidor`). El toggle en `/operario/repartidores/` sigue el mismo patrón ya implementado para comercios (HU 16/27): `POST /operario/repartidores/estado/` con `username` y `activo`, bloqueando la desactivación con el mensaje `"El repartidor tiene pedidos en curso"` si el repartidor tiene un pedido en estado `asignado`, `retirado` o `en_viaje`. La reactivación no exige esa validación. |
| 2026-11-13 | HU 30 — Alerta de pedido sin repartidor | Aprobado para la implementación: `Pedido.vehiculo_requerido` deja de ser texto libre y pasa a un selector de opciones cerradas con las de `Repartidor.VEHICULOS` (`bicicleta`, `moto`, `auto`, `camion`), conservando la lectura de valores históricos (texto libre o vacío se muestra tal como está o como “No informado”). El despacho automático es un servicio reutilizable que elige un repartidor con usuario activo, `disponible=True`, sin pedido en curso (`asignado`, `retirado`, `en_viaje`) y vehículo exactamente igual al pedido requerido; desempata por el que hace más tiempo no tiene viaje, priorizando a quienes nunca tuvieron viaje y usando el `pk` como último criterio. Si no hay candidato, el pedido queda `registrado` sin repartidor y se activa la alerta “Pedido sin repartidor disponible”, con notificación flotante en el panel, aviso en el detalle y el botón POST “Reintentar asignación” (`operario:reintentar_asignacion`). La asignación manual se conserva y sus opciones se filtran por el vehículo requerido. |
| 2026-11-13 | HU 30 — Reasignación automática en cascada | Aprobado para la implementación: al rechazar o expirar la espera, la liberación (`estado='registrado'`, `repartidor=None` y repartidor `disponible=False`) va seguida, dentro de la misma transacción, de una nueva invocación del despacho automático con el usuario actor. Si hay otro candidato compatible, el pedido se reasigna (`asignado`, nuevo `fecha_hora_asignacion` y evento de asignación automática) y no se muestra la alerta; solo si se agotan los candidatos queda `registrado` con la alerta “Pedido sin repartidor disponible” y el reintento manual. La expiración también se procesa al consultar `inicio`, `estado_pedidos` y `detalle_pedido` del operario. El servicio compartido vive en `Backend/main/despacho.py`. |
| 2026-11-13 | HU 30 — Cola FIFO por tiempo de espera | Aprobado para la implementación: se agrega `Repartidor.disponible_desde` (migración `repartidor.0012`) y el despacho automático ordena por ese timestamp ascendente (`F('disponible_desde').asc(nulls_last=True)`) con desempate por `pk`, sin excluir por historial de rechazos. El valor se registra al pasar a disponible (toggle, fin de entrega `entregado`/`fallido`, cancelación de un pedido asignado) y se limpia al pasar a no disponible; `Repartidor.save()` lo inicializa si se guarda `disponible=True` sin timestamp. Un repartidor que rechaza o expira pierde su lugar y, al volver a marcarse disponible, recibe un timestamp nuevo y queda al final de la cola. |

La interfaz de carga y las consultas públicas se implementan con las plantillas Django existentes; no se aprobó incorporar un framework frontend independiente. Los campos nuevos permanecen opcionales en la base para mantener compatibilidad de filas antiguas, aunque el formulario de alta los requiere.

## Hechos de configuración, no decisiones de arquitectura

- `Backend/config/settings.py` configura SQLite para desarrollo local.
- `requirements.txt` fija las versiones actuales de Django y sus dependencias.
- `Frontend/` sigue siendo un marcador de posición; no hay framework elegido en sus archivos.

## Pendiente de confirmación del equipo

- Base de datos compartida y proveedor; PostgreSQL figuraba como propuesta previa, no como acuerdo.
- Arquitectura y tecnologías de la interfaz.
- Plataformas/arquitectura objetivo (la inicialización declara “Pendiente de definir”). La Entrevista 02 describe PC web o escritorio para operario y web móvil para repartidor, pero no consta una elección tecnológica posterior del equipo.
- Despliegue, seguridad de producción y manejo de archivos/fotografías.
- Alcance y prioridad de las historias y fechas vigentes de los sprints.
- HU 22: los criterios de asignación automática que no se cubrieron con HU 30 (incluida la cercanía) quedan diferidos. La asignación manual del operario se conserva como alternativa y convive con el despacho automático implementado en HU 30.
- HU 30: el criterio original de “candidatos disponibles y cercanos” para el reintento no se implementó porque el modelo no registra ubicación suficiente para calcularla; la regla acordada en esta etapa se limita al vehículo, la disponibilidad y la ausencia de viaje en curso. Confirmar con el equipo si la cercanía debe incorporarse más adelante.
- HU 18: el código registra rechazo/expiración en `HistorialEstado`, pero no envía una notificación activa al operario aunque ese paso aparece en el criterio de aceptación. Falta acordar e implementar el canal de notificación.
- HU 18: la expiración de cinco minutos se evalúa de forma perezosa al cargar la vista del repartidor o responder a la solicitud, y ahora también al consultar el panel del operario (`inicio`, `estado_pedidos`, `detalle_pedido`); la liberación en segundo plano requeriría una tarea programada.
- HU 18: la aceptación deja el pedido en `asignado`, registra la hora de aceptación y habilita la acción existente de retiro; `retirado` se conserva como transición posterior. Esta interpretación mantiene el criterio de aceptación y el flujo de estados implementado en el backend. Confirmar con el equipo si se requiere un estado distinto para la confirmación.
- Para una futura migración productiva, ensayar el esquema contra una copia autorizada con pedidos heredados: en este entorno no existía una base poblada para validar sus datos reales.

Al cerrar una decisión, agregá fecha, contexto, opciones consideradas, acuerdo y fuente o acta que lo respalda.
