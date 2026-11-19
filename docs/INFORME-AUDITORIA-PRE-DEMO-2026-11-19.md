# Auditoría pre-demo — 2026-11-19

## Alcance y evidencia

Se inspeccionaron los documentos de `docs/`, el código Django, rutas, modelos, formularios, plantillas, configuración, migraciones y las exportaciones sanitizadas/CSV incluidas. El snapshot Taiga del 19/11/2026 contiene 31 historias, 7 épicas y 2 hitos; las 31 historias figuran `Done`. No se consultó Taiga en vivo. La exportación original no está en el repositorio; la síntesis se basa en el derivado sanitizado y el CSV versionados.

Se ejecutó la suite Django completa (182 pruebas) sobre SQLite en memoria. Se hizo un recorrido visual parcial en un navegador, en una base descartable: portada pública, panel/detalle del operario, lista y filtro de comercios, lista/modal de PIN, login y recorrido completo del repartidor, y seguimiento público final. No se inspeccionaron todas las pantallas ni un viewport de escritorio ancho. La SQLite `Backend/db.sqlite3` existía y no se modificó. Neon no tenía URL/credenciales en el entorno, por lo que no se conectó ni se migró una base externa. El intérprete disponible fue Python 3.13.16; el repositorio declara la serie 3.14.

## A. Resumen ejecutivo

- **Preparación:** apta para una demo local controlada después de ensayar los datos y los recorridos indicados abajo. No se considera lista para producción ni para una demo conectada a Neon sin comprobar la URL y ejecutar migraciones en una base autorizada.
- **Export Taiga:** 31/31 en estado `Done` en el snapshot. Eso no equivale a verificación funcional.
- **Auditoría:** una falla reproducible de configuración encontrada y corregida; cero fallos o errores en las 182 pruebas. No se realizó una auditoría visual completa ni una prueba de penetración.
- **Bugs corregidos:** 1 (P2, selección silenciosa de SQLite ante `DATABASE_URL` con esquema inválido).
- **Pendientes con impacto:** HU 18 no envía notificación activa al operario al rechazo; el login por PIN no limita intentos; Neon y pantallas autenticadas no se verificaron en esta máquina.
- **Cambio de código:** `Backend/config/settings.py` ahora falla con `ImproperlyConfigured` ante un `DATABASE_URL` no vacío que no use `postgres://` o `postgresql://`. Así se evita que una URL mal escrita mande operaciones a SQLite sin aviso.

## B. Matriz HU → implementación → pruebas

La columna “prueba/evidencia” indica cobertura automatizada y código contrastado; las pruebas manuales parciales no equivalen a una ejecución independiente de cada criterio. “Observaciones” señala el límite comprobado o la falta de inspección visual del comportamiento indicado. Los IDs y títulos corresponden al snapshot local.

| HU | Sprint | Estado inicial | Resultado y evidencia | Corrección de esta auditoría | Estado final |
|---|---|---|---|---|---|
| 9 — Iniciar sesión operario | 1 | Presente; Taiga `Done` | Login y redirección por rol: `homePage.tests.PortadaYAccesosTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 10 — Registrar comercios | 1 | Presente; Taiga `Done` | Formularios, duplicados y permisos en `ComerciosOperarioTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 11 — Alta de repartidor | 1 | Presente; Taiga `Done` | Alta transaccional, DNI/PIN, vehículo y valores opcionales en `RepartidoresOperarioTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 12 — Cargar pedido nuevo | 1 | Presente; Taiga `Done` | Validación, comercio activo, idempotencia, código e historial en `CargarPedidoTests` y `CargarPedidoValidacionesTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 13 — Cancelar pedido | 2 | Presente; Taiga `Done` | Estados permitidos, POST, permisos, historial y liberación en `CancelarPedidoTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 14 — Ver historial de cambios | 2 | Presente; Taiga `Done` | Timeline, fotos y protección del historial en `PanelOperarioTests` y `HistorialInmutabilidadAdminTests` | Ninguna | Implementada; visualización modal no revisada manualmente |
| 15 — Visualizar repartidores activos | 2 | Presente; Taiga `Done` | Lista, endpoint y actualización de disponibilidad en `EstadoRepartidoresTests` | Ninguna | Implementada; sondeo no revisado visualmente en navegador |
| 16 — Deshabilitar comercio | 2 | Presente; Taiga `Done` | Borrado lógico, alta de pedidos e historial en `ComerciosOperarioTests`/`CargarPedidoValidacionesTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 17 — Acceso con PIN | 1 | Presente; Taiga `Done` | PIN válido/inválido, perfil y usuario activo en `DisponibilidadRepartidorTests` | Ninguna | Implementada; no tiene limitación de intentos |
| 18 — Aceptar asignación | 1 | Presente; Taiga `Done` | Aceptar, rechazar, timeout, historial y cascada en `AsignacionConRespuestaTests` | No se agregó canal de notificación porque requiere decisión/alcance | Implementada con observaciones: no notifica activamente al operario; expiración es perezosa |
| 19 — Actualizar estado de entrega | 1 | Presente; Taiga `Done` | Transiciones, motivo, evidencia y atomicidad en `ActualizarEstadoTests`/`FotografiasEntregaTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 20 — Cambiar disponibilidad | 1 | Presente; Taiga `Done` | Persistencia, permisos y restricción con pedido activo en `DisponibilidadRepartidorTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 21 — Ingresar código seguimiento | 1 | Presente; Taiga `Done` | Búsqueda válida/inválida, 404 y solo lectura en `SeguimientoPersistidoTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 22 — Visualizar datos del viaje | 1 | Presente; Taiga `Done` | Detalles, cronómetro y cierre de asignación en pruebas de `AsignacionConRespuestaTests` y `DetalleRepartidorTests` | Ninguna | Implementada; pantalla no revisada manualmente |
| 23 — Filtrar historial de pedidos | 2 | Presente; Taiga `Done` | Filtros, comercios inactivos y cero resultados en `HistorialPedidosFiltrosTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 24 — Visualizar estado del pedido | 1 | Presente; Taiga `Done` | Estados, ETA y ocultamiento en estados finales en `SeguimientoPersistidoTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 25 — Editar comercio | 2 | Presente; Taiga `Done` | Edición, nombre duplicado y estado en `ComerciosOperarioTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 26 — Listar pedidos en curso | 1 | Presente; Taiga `Done` | Orden, contenido y refresco del panel en `PanelOperarioTests` | Ninguna | Implementada; refresco no observado en navegador |
| 27 — Reactivar comercio | 2 | Presente; Taiga `Done` | Confirmación y estado en `ComerciosOperarioTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 28 — Consultar comercios | 2 | Presente; Taiga `Done` | Búsqueda, filtro y estado en `ComerciosOperarioTests` | Ninguna | Correctamente implementada; vista no inspeccionada manualmente |
| 29 — Deshabilitar repartidor | 2 | Presente; Taiga `Done` | Restricción por pedidos activos, login y reactivación en `CambiarEstadoRepartidorTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 30 — Alerta sin repartidor | 2 | Presente; Taiga `Done` | Aviso, persistencia y reintento en `AlertaSinRepartidorTests` | Ninguna | Implementada; notificación flotante no revisada visualmente |
| 32 — Recuperar PIN | 2 | Presente; Taiga `Done` | Unicidad, formato, rechazo, invalidación y permisos en `RepartidoresOperarioTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 33 — Detalle de pedidos | 2 | Presente; Taiga `Done` | Campos, historial, estados vacíos y permiso en `PanelOperarioTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 34 — Ver fallidos/devolución | 2 | Presente; Taiga `Done` | Lista, evidencia, actor/fecha, POST e idempotencia en `EntregasFallidasTests` | Ninguna | Implementada con observaciones: orden y una recepción por pedido son decisiones pendientes de validar |
| 35 — Información pedido activo | 1 | Presente; Taiga `Done` | Comercio/dirección de retiro/destino/acciones en `AsignacionConRespuestaTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 36 — Registrar entrega fallida | 1 | Presente; Taiga `Done` | Motivo requerido, foto opcional, permisos y transición en `FotografiasEntregaTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 38 — Historial público | 1 | Presente; Taiga `Done` | Orden cronológico y omisión de datos internos/fotos en `SeguimientoPersistidoTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 40 — Listar pedidos del repartidor | 1 | Presente; Taiga `Done` | Filtrado por propietario y orden en `HistorialEntregasTests` | Ninguna | Correctamente implementada en pruebas automatizadas |
| 41 — Asignación automática | 2 | Presente; Taiga `Done` | FIFO, compatibilidad y elegibilidad en `DespachoAutomaticoTests`; cascada en `CascadaReasignacionTests` y `ColaFifoReasignacionTests` | Ninguna | Correctamente implementada según criterios del snapshot |
| 42 — Reintentar asignación | 2 | Presente; Taiga `Done` | Éxito/falta de candidatos, estado y permisos en `AlertaSinRepartidorTests` | Ninguna | Correctamente implementada en pruebas automatizadas |

No aparece una HU completamente ausente en el código inspeccionado. Esto no certifica todos los criterios en uso real: faltó la ronda visual manual y la comprobación con Taiga en vivo.

## C. Bug corregido

| ID | Descripción y causa | Severidad | Solución | Prueba de verificación |
|---|---|---|---|---|
| CFG-01 | Un `DATABASE_URL` no vacío con esquema no soportado caía silenciosamente al bloque SQLite. Una URL de Neon mal copiada podía dirigir escrituras a `Backend/db.sqlite3`. | P2 | `settings.py` ahora rechaza esquemas distintos de `postgres://`/`postgresql://` con `ImproperlyConfigured`; la variable vacía mantiene SQLite. | `DATABASE_URL='sqlite:///wrong.db' ... manage.py check` falla con el mensaje esperado; variable vacía pasa con `settings.py`; URL PostgreSQL de prueba selecciona `django.db.backends.postgresql` sin conectarse. |

## D. Problemas pendientes y riesgos

- **HU 18:** falta la notificación activa al operario tras rechazo. No se implementó porque falta definir canal y comportamiento. La reasignación automática sí se ejecuta al procesar el rechazo/expiración.
- **Seguridad:** no se encontró limitación de intentos para el login de PIN. Los PIN se almacenan en texto según la decisión registrada de HU 32. Mitigar antes de exponer el sistema; mantener la demo en un entorno controlado.
- **Neon:** sin `.env` ni credenciales no se probaron conectividad, migraciones ni el recorrido real. Las instrucciones están documentadas, pero el integrante debe verificar que la cadena apunta a una base de desarrollo antes de `migrate`.
- **Visual:** se recorrieron algunas pantallas a 663×711; falta escritorio ancho, otros tamaños y las páginas no visitadas (por ejemplo, formularios de alta, historial completo y entregas fallidas). Ensayar los flujos visuales prioritarios antes de presentar.
- **Entorno:** suite ejecutada en Python 3.13.16, mientras `.python-version` fija 3.14. No se pudo usar el `.venv` existente porque su intérprete 3.14 no está disponible en este host.
- **HU 34:** el sistema presenta fallidos por fecha ascendente y registra una devolución por pedido. Validar orden y cardinalidad con el equipo.
- **Producción:** `DEBUG=True`, clave de desarrollo, archivos locales y ausencia de controles de despliegue; no usar la configuración actual fuera del entorno de desarrollo.
- **Automatización:** no se ejecutaron pruebas de ataques reales de XSS, SQLi, CSRF externo, concurrencia bajo carga, sesiones vencidas en navegador ni fallos de red.

## E. Documentación actualizada

Se actualizaron `readme.md`, `docs/PROJECT_BRIEF.md`, `docs/KNOWLEDGE_BASE.md`, `docs/GUIA-EJECUCION-Y-PRUEBAS.md`, `docs/MANUAL-DE-USO.md` y `docs/DECISIONS.md`; se añadió este informe y se enlaza desde `docs/INDEX.md`. No se fusionó ni eliminó documentación o material académico. La guía describe SQLite y Neon: instalación, `DATABASE_URL`, selección, conexión, migraciones, inicio, verificación y errores habituales. La ruta Neon está documentada a partir de la implementación, pero no se probó en vivo.

## F. Verificaciones ejecutadas

- `python manage.py test --settings=config.settings_test` — 182 pruebas, aprobadas; cero fallos y errores. La prueba corrió con Python 3.13.16, Django 6.1.2 y SQLite en memoria.
- `python manage.py check --settings=config.settings_test` — aprobado.
- `python manage.py makemigrations --check --dry-run --settings=config.settings_test` — “No changes detected”.
- `python -m pip check` — sin dependencias incompatibles.
- `python3 scripts/check_docs.py .` — 48 enlaces locales verificados en la revisión final.
- Configuración real: SQLite con `DATABASE_URL=''` pasó `manage.py check`; URL PostgreSQL de prueba seleccionó el motor PostgreSQL sin conexión; esquema no admitido falló rápido como se esperaba.
- Seguridad automatizada: la suite cubre permisos de operario, propiedad de pedidos/evidencias, métodos HTTP, validaciones de imagen, estados e inmutabilidad del historial. No equivale a prueba de penetración.
- Prueba manual en navegador con base SQLite temporal: login de operario y repartidor; visualización de pedido activo; aceptación, retiro, inicio de viaje y entrega; seguimiento público. Se verificó que la pantalla pública muestra estado e historial sin exponer nombre/teléfono del repartidor ni evidencia.
- Inspección visual parcial: portada, panel y detalle de operario, filtro de comercios (incluido “sin coincidencias”), lista y modal de regeneración de PIN, panel del repartidor y cronología pública. Resolución observada 663×711; no se revisó escritorio ancho ni todas las páginas.

## G. Recomendación para la demo

El proyecto se puede presentar en una demo local, luego de aplicar migraciones al entorno elegido y ensayar con registros ficticios. Está verificada por pruebas automatizadas la lógica principal de las HUs de Sprint 2 listadas en la matriz, incluyendo comercios, cancelación, filtros, roles, despacho FIFO, alerta/reintento, HU 32–34 y detalle.

Antes del ensayo, probar: login de operario; alta/edición y baja lógica de comercio; alta y PIN de repartidor; carga con automático y sin candidato; aceptación/rechazo y cascada; un ciclo retirado→en viaje→entregado y uno fallido/devolución; tracking público; acceso directo por rol. Si la demo depende de Neon, ejecutar primero conexión y migraciones contra la base de desarrollo elegida.

No presentar el sistema como listo para producción. La notificación activa HU 18, la protección contra intentos repetidos de PIN y la conexión real de Neon siguen pendientes. También queda una revisión visual de las páginas no recorridas y de un viewport de escritorio.
