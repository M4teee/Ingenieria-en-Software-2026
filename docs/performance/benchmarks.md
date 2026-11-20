# Benchmarks

Fecha: 20/11/2026.

## Comparación antes/después

| Medida | Antes | Después | Estado |
|---|---:|---:|---|
| FCP, LCP, INP, CLS | Sin medir | Sin medir | No hubo navegador conectado a localhost. |
| TTFB y respuesta de vistas | Sin medir | Sin medir | No se tomó una muestra HTTP de navegador. |
| Solicitudes y bytes de red | Sin medir | Sin medir | No se pudo abrir Network Profiler. |
| Consultas SQL por pantalla | Sin medir | Sin medir | No se instrumentó una sesión de profiling. |
| Reconstrucción DOM de tabla sin cambios | Una vez por respuesta de sondeo | Solo ante cambio en la respuesta | Verificado por inspección del código; no se midió CPU/tiempo. |
| Geometría CSS declarada del input | `min-height: 3.5rem` + padding vertical | `height: 3.5rem`, padding horizontal y line-height explícita | Declaración revisada; screenshot no disponible. |

No hay cifras de rendimiento comparables en milisegundos. La vista previa de capturas del repositorio no sustituye a una captura de la aplicación en ejecución, así que no se presenta como benchmark.
