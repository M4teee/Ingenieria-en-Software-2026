# Base de conocimiento

Síntesis para orientación. Los documentos originales y la implementación tienen prioridad; ver [`SOURCE_INDEX.md`](SOURCE_INDEX.md) y [`CURRENT_STATE.md`](CURRENT_STATE.md).

## Confirmado en las fuentes disponibles

- El proyecto académico es un Sistema de Gestión de Repartos para coordinar comercios, operario, repartidores y consulta de clientes finales.
- Las fuentes describen siete épicas y siete estados de pedido. La exportación Taiga sanitizada y versionada contiene 28 historias y dos hitos de sprint; no es el tablero en vivo.
- El backend actual usa Django y SQLite. En la rama de HU 12, `Pedido` se asocia con `Comercio`, se registra desde la interfaz protegida del operario y se consulta por su código en el seguimiento público; `HistorialEstado` alimenta la cronología. El repartidor puede avanzar pedidos previamente asignados.
- Las historias y el PGP expresan alcance y planificación, no entregables ya implementados.

## Discrepancias y límites

- La exportación disponible contiene 28 historias, mientras una nota anterior decía 29. No se puede determinar cuál falta ni consultar el tablero en vivo con las fuentes versionadas; confirmar con el equipo cuando sea posible.
- El PGP describe el plan de dos sprints y una entrega el 20/11/2026. No se comprobó el avance real ni la vigencia del calendario.
- No se encontró la consigna general ni presentaciones de la cátedra en la carpeta de contexto.
- El frontend, la base de datos compartida y el despliegue siguen sin decisión registrada.
- La Entrevista 02 describe PC web o escritorio para el operario y web móvil para el repartidor; la tecnología/plataforma objetivo elegida por el equipo sigue pendiente.
- El panel del operario dispone de asignación manual provisional a repartidores activos y disponibles. Las HU 22/30 de asignación automática y cercanía siguen pendientes. El sistema tampoco garantiza historial inmutable ni operación sin conexión; esos requisitos requieren trabajo posterior.
- La Entrevista 02 enumera siete estados y el PGP lista cuatro en su sección de definiciones; el modelo actual contempla siete según la entrevista y HU 12, pero el alcance de operaciones todavía incompletas debe confirmarse con el equipo.
- Estimaciones, responsables y alcance comprometido de cada sprint.
