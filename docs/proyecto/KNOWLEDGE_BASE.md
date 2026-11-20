# Base de conocimiento

Síntesis para orientación. Los documentos originales y la implementación tienen prioridad; ver [`SOURCE_INDEX.md`](SOURCE_INDEX.md), [`CURRENT_STATE.md`](CURRENT_STATE.md) y el [informe de auditoría pre-demo](INFORME-AUDITORIA-PRE-DEMO-2026-11-19.md).

## Confirmado en las fuentes disponibles

- El proyecto académico es un Sistema de Gestión de Repartos para coordinar comercios, operario, repartidores y consulta de clientes finales.
- Las fuentes describen siete épicas y siete estados de pedido. La exportación Taiga sanitizada y versionada del 19/11/2026 contiene 31 historias y dos hitos de sprint; no es el tablero en vivo. Las 31 historias figuran como `Done` en ese snapshot.
- El backend usa Django y configura SQLite local si `DATABASE_URL` está vacía, o PostgreSQL si contiene una URL `postgres://` o `postgresql://`; esa ruta también admite la conexión de Neon. `Frontend/` no es una app frontend independiente.
- La interfaz del operario usa `is_operario`. El personal con `is_staff` conserva acceso separado a Django Admin. El repartidor inicia sesión con un PIN de cuatro dígitos.
- HU 41 implementa despacho automático FIFO con filtros de vehículo, disponibilidad y pedidos activos; HU 30 muestra una alerta cuando no hay candidato y HU 42 permite reintentar. HU 22 trata la información y el contador que se presentan al repartidor durante la asignación.

## Discrepancias y límites

- No se consultó Taiga en vivo. Confirmar si hubo cambios posteriores al snapshot del 19/11/2026.
- HU 18 no envía notificación activa al operario ante un rechazo; la expiración de cinco minutos se procesa al consultar o responder, no con una tarea en segundo plano.
- No se calcula cercanía geográfica. Las HUs 41 y 42 del snapshot definen FIFO por tiempo disponible y compatibilidad, sin pedir ubicación.
- HU 34 admite una sola confirmación de devolución por pedido. Validar con el equipo si el proceso real admite múltiples recepciones y qué dirección de orden por fecha prefiere.
- El modo offline, el despliegue, HTTPS y la protección contra fuerza bruta del PIN no se consideran verificados para producción. La configuración Django es de desarrollo.
- En la auditoría del 19/11 no había credenciales `.env` para probar Neon. Se revisó visualmente una selección de páginas autenticadas en navegador con base temporal, pero no todas las pantallas ni escritorio ancho. La suite y los chequeos locales pasaron con Python 3.13.16, aunque el proyecto declara Python 3.14.
- El PGP, revisión 1.0 del 04/10/2026, propone dos sprints y una entrega el 20/11/2026; es planificación documental y no prueba avance ni vigencia del calendario.
- No se encontró la consigna general ni presentaciones de cátedra en la carpeta de contexto.
