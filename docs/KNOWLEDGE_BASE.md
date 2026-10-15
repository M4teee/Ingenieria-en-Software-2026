# Base de conocimiento

Síntesis para orientación. Los documentos originales y la implementación tienen prioridad; ver [`SOURCE_INDEX.md`](SOURCE_INDEX.md) y [`CURRENT_STATE.md`](CURRENT_STATE.md).

## Confirmado en las fuentes disponibles

- El proyecto académico es un Sistema de Gestión de Repartos para coordinar comercios, operario, repartidores y consulta de clientes finales.
- Las fuentes describen siete épicas y siete estados de pedido. La exportación Taiga sanitizada y versionada contiene 28 historias y dos hitos de sprint; no es el tablero en vivo.
- El backend actual usa Django y SQLite; además de los modelos de comercio, usuario y vehículo, hay modelos persistentes `Pedido` e `HistorialEstado` y un flujo autenticado de actualización de estado del repartidor. El seguimiento público aún usa pedidos simulados, sin conexión con esos modelos.
- Las historias y el PGP expresan alcance y planificación, no entregables ya implementados.

## Discrepancias y límites

- La exportación disponible contiene 28 historias, mientras una nota anterior decía 29. No se puede determinar cuál falta ni consultar el tablero en vivo con las fuentes versionadas; confirmar con el equipo cuando sea posible.
- El PGP describe el plan de dos sprints y una entrega el 20/11/2026. No se comprobó el avance real ni la vigencia del calendario.
- No se encontró la consigna general ni presentaciones de la cátedra en la carpeta de contexto.
- El frontend, la base de datos compartida y el despliegue siguen sin decisión registrada.
- La Entrevista 02 describe PC web o escritorio para el operario y web móvil para el repartidor; la tecnología/plataforma objetivo elegida por el equipo sigue pendiente.
- El modelo persistente solo contempla cinco estados del pedido, mientras la Entrevista 02 define siete. No se observó generación de códigos de seguimiento, el flujo operativo de alta/asignación, la integración con el comercio y el seguimiento público, ni garantías de inmutabilidad del historial. Estas son discrepancias observadas entre fuentes y código, no decisiones para cambiar el comportamiento.
- La Entrevista 02 enumera siete estados y el PGP lista cuatro en su sección de definiciones; no queda claro si el PGP describe solo los estados de la etapa del repartidor. Confirmar alcance y transiciones antes de implementar el ciclo completo.
- Estimaciones, responsables y alcance comprometido de cada sprint.
