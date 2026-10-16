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
- HU 22/30 no implementadas: sus criterios de asignación automática (incluida la cercanía donde corresponde) quedan diferidos. La asignación manual es solo un puente provisional y no satisface ni completa esas historias.
- HU 18: el código registra rechazo/expiración en `HistorialEstado`, pero no envía una notificación activa al operario aunque ese paso aparece en el criterio de aceptación. Falta acordar e implementar el canal de notificación.
- HU 18: la expiración de cinco minutos se evalúa de forma perezosa al cargar la vista del repartidor o responder a la solicitud; la liberación en segundo plano requeriría una tarea programada.
- HU 18: la aceptación deja el pedido en `asignado`, registra la hora de aceptación y habilita la acción existente de retiro; `retirado` se conserva como transición posterior. Esta interpretación mantiene el criterio de aceptación y el flujo de estados implementado en el backend. Confirmar con el equipo si se requiere un estado distinto para la confirmación.
- Para una futura migración productiva, ensayar el esquema contra una copia autorizada con pedidos heredados: en este entorno no existía una base poblada para validar sus datos reales.

Al cerrar una decisión, agregá fecha, contexto, opciones consideradas, acuerdo y fuente o acta que lo respalda.
