# Optimizaciones

Fecha: 20/11/2026.

## Aplicadas

- **Seguimiento público:** el input ahora ocupa una caja de 3.5rem con `box-sizing: border-box`, elimina el padding vertical que dependía de métricas nativas y define `line-height: 1.25`. Se conserva su ancho, alto visual, tipografía, tamaño de texto, colores, borde y radio. La intención es centrar de forma estable placeholder, texto y cursor, evitando que el padding sume altura a la caja.
- **Panel del operario:** la tabla solo reemplaza sus filas, actualiza contadores y aplica filtros cuando cambia la respuesta JSON. El sondeo y su intervalo de cinco segundos siguen iguales; continúan las actualizaciones de conexión, hora y avisos.

La primera mejora apunta a consistencia visual y no supone una reducción de tiempo de carga medible. La segunda reduce reconstrucciones de nodos y trabajo de renderizado cuando el estado se mantiene; su impacto en milisegundos no se midió en este entorno.

## Ya existente y preservado

Se conservaron carga diferida de scripts, carga de relaciones en consultas del panel, índices `0013_perf_indexes`, sondeo condicionado por visibilidad y transformación de la barra de asignación. No se agregaron paquetes al manifiesto ni se alteró el comportamiento de negocio.
