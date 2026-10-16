# Brief del proyecto

Actualizado: 2026-10-15. Síntesis de las fuentes originales listadas en [`SOURCE_INDEX.md`](SOURCE_INDEX.md); no sustituye esas fuentes ni el tablero vigente.

## Propósito y actores

El Sistema de Gestión de Repartos (SGR) busca centralizar la carga y el seguimiento de pedidos y distribuir tareas que hoy recaen en un operario. Las entrevistas identifican cuatro actores: operario, repartidor, comercio y cliente final. En el flujo relevado, el comercio solicita pedidos por WhatsApp al operario; el cliente final consulta el envío con un código y sin cuenta.

## Alcance descrito por las fuentes

Las siete épicas cubren: alta y gestión de comercios; ciclo de vida de pedidos; disponibilidad de repartidores; asignación de viajes; operación móvil con evidencia fotográfica; seguimiento público; historial y auditoría. La Entrevista 02 enumera los estados `registrado`, `asignado`, `retirado`, `en viaje`, `entregado`, `fallido` y `cancelado`. También indica que se permite cancelar antes del retiro, que un repartidor lleva un pedido por vez y que el código de seguimiento no debe ser predecible. El PGP lista cuatro estados en su sección de definiciones; las fuentes no aclaran si se refiere solo a la parte operativa del repartidor.

Los requisitos no funcionales piden interfaces web diferenciadas para escritorio y móvil, pocos pasos para operar, compresión de fotos, tolerancia a cortes de conectividad, historial inmutable, HTTPS, registro de fallas y separación de interfaz y lógica. Son objetivos de requisitos; no están implementados ni verificados íntegramente en el código actual.

## Base técnica observada

El repositorio fija Python 3.14 en `.python-version` y Django 6.1.2 en `requirements.txt`. La configuración actual usa SQLite. `Frontend/` no tiene una aplicación implementada. El estado funcional está descrito en [`CURRENT_STATE.md`](CURRENT_STATE.md); las decisiones abiertas están en [`DECISIONS.md`](DECISIONS.md).

## Diferencia entre requisitos y producto actual

El backend mantiene modelos persistentes `Pedido` e `HistorialEstado`. En la rama actual, el operario registra pedidos asociados a comercios activos, con estado inicial `registrado`, código seguro, fecha estimada y evento de historial. La consulta pública busca pedidos por el código persistido; el repartidor puede avanzar un pedido previamente asignado y guardar los cambios en el historial con fotografía opcional al retirar o entregar.

La asignación a repartidores todavía no tiene interfaz. Las entrevistas describen siete estados y reglas de cancelación antes del retiro; el modelo contempla esos estados, pero no todas las operaciones cuentan con una pantalla. Los requisitos no funcionales listados arriba tampoco están implementados ni verificados íntegramente. Las historias fuera del alcance implementado no deben presentarse como funcionalidades disponibles.

## Plan académico

El PGP, revisión 1.0 del 4 de octubre de 2026, propone dos sprints y una entrega final el 20 de noviembre de 2026. Es planificación documental, no comprobación del progreso. El export de Taiga disponible registra 28 historias y 7 épicas; una nota anterior decía 29 historias. Confirmar la cantidad y el estado actuales en Taiga.
