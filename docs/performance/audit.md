# Auditoría de rendimiento

Fecha: 20/11/2026.

## Alcance y método

Se inspeccionaron las plantillas compartidas, CSS y JavaScript, las vistas de cliente, operario y repartidor, los QuerySets y los modelos relevantes. El entorno permite iniciar Django, pero el navegador disponible no pudo conectarse a `localhost`; no se obtuvieron perfiles de Chrome, métricas Core Web Vitals ni capturas reales. No se asignan valores estimados a esas métricas.

## Hallazgos

- La vista del panel del operario ya limita la lista a pedidos en curso y carga comercio y repartidor con `select_related`. La respuesta JSON de actualización consulta de nuevo esa lista cada cinco segundos.
- El cliente recibía y parseaba el estado completo en cada sondeo. Aunque los datos no cambiasen, JavaScript reemplazaba todas las filas de la tabla, causando trabajo de DOM y rendering innecesario.
- El CSS del seguimiento establece `min-height` junto con padding vertical para un input nativo, pero no fija `box-sizing`, altura ni `line-height`. El resultado depende de estilos heredados y métricas nativas, origen plausible del descentrado y el contacto con el divisor.
- La vista de inicio del repartidor ya limita el sondeo a pestañas visibles y evita solapar una subida/formulario mediante condiciones en cliente. El contador transforma su barra con `scaleX`.
- La mayoría de los accesos a relaciones que se usan en plantillas ya están optimizados con `select_related`/`prefetch_related`. El proyecto incluye índices específicos para pedidos activos, vencimientos y candidatos de despacho en la migración `0013_perf_indexes`.
- Las hojas y scripts compartidos se sirven localmente; los scripts van con `defer`. La fuente Archivo/IBM Plex Mono se carga desde Google Fonts y constituye una dependencia de red externa.
- El historial general no pagina, como ya registra `docs/estado.md`; corregirlo cambiaría el flujo visible y no se hizo en esta optimización acotada.

## Límites de evidencia

No se midieron FCP, LCP, INP, CLS, TTFB, solicitudes de red, bytes transferidos, CPU ni tiempos SQL. Tampoco se pudo inspeccionar el input en los tamaños responsive indicados con un navegador conectado. Los cuellos de botella de tabla y métricas CSS se identificaron por lectura del código y se verifican con las pruebas funcionales disponibles, no con profiling visual.
