# Estado del proyecto

Actualizado: 20/11/2026, rama `feature/rediseno-frontend`.

## Resumen

Las 31 historias del backlog (exportación de Taiga del 19/11/2026, ver [fuentes](fuentes/README.md)) tienen implementación en el código. La interfaz se rediseñó por completo sobre plantillas Django. La configuración es de desarrollo y no está lista para producción ([SECURITY.md](../SECURITY.md)).

## Cobertura del backlog

| Área | Historias | Dónde |
|---|---|---|
| Acceso | 9 ingreso del operario · 17 ingreso por PIN | `/login/`, `/repartidor/login-pin/` |
| Comercios | 10 alta · 16 deshabilitar · 25 editar · 27 reactivar · 28 listado | `/operario/comercios/` |
| Repartidores | 11 alta · 15 activos y disponibilidad en vivo · 29 deshabilitar · 32 regenerar PIN | `/operario/repartidores/` |
| Pedidos (operario) | 12 cargar · 13 cancelar · 14 historial de cambios con fotos · 23 filtrar historial · 26 en curso · 33 detalle · 34 fallidos y devolución | `/operario/`, `/operario/pedidos/…` |
| Asignación | 18 aceptar o rechazar · 22 datos y tiempo de la asignación · 30 alerta sin repartidor · 41 despacho automático · 42 reintento | `main/despacho.py`, panel del operario y del repartidor |
| Reparto | 19 actualizar estado · 20 disponibilidad · 35 pedido activo · 36 entrega fallida · 40 historial de entregas | `/repartidor/` |
| Seguimiento | 21 código de seguimiento · 24 estado · 38 historial de estados | `/`, `/clienteFinal/seguimiento/<código>/` |

## Decisiones vigentes

- **Roles:** el acceso a `/operario/` depende de `User.is_operario`, independiente de `is_staff` (que solo habilita Django Admin). La migración `users.0004` conservó el acceso de las cuentas que ya eran staff.
- **Baja de repartidor:** se usa `User.is_active` como baja lógica; no hay un campo propio en `Repartidor`. No se puede desactivar a quien tiene un pedido en curso.
- **Disponibilidad:** la fuente única es `Repartidor.disponible` (con `disponible_desde`); se eliminó la propiedad calculada de `User`.
- **Despacho FIFO:** candidato = usuario activo, disponible, mismo vehículo exacto y sin pedido en curso, ordenado por `disponible_desde`. Sin cálculo de cercanía: el modelo no registra ubicación.
- **Asignación:** el repartidor tiene 5 minutos para responder. Al vencer, el pedido vuelve a `registrado`, el repartidor queda no disponible y se reintenta el despacho. El vencimiento se evalúa al cargar los paneles (no hay tareas en segundo plano).
- **PIN:** 4 dígitos, únicos, guardados como texto para que el operario pueda comunicarlos; el operario ingresa el nuevo PIN al regenerarlo.
- **Devolución:** registro inmutable `Devolucion` (uno por pedido fallido), separado de `HistorialEstado`; el pedido sigue en `fallido`.
- **Seguimiento público:** muestra estado, comercio, historial y la hora estimada solo en `en_viaje`; nunca destinatario, repartidor ni fotos.
- **Fuera de alcance del MVP:** modo offline (RNF 7) y notificaciones externas.
- **Base de datos:** SQLite por defecto; PostgreSQL/Neon con `DATABASE_URL`, pool de conexiones propio (`config/pool.py`), sesiones `cached_db` y autenticación cacheada para reducir viajes a la base remota.
- **Interfaz:** plantillas Django con Basecoat UI incluido en el repositorio y sin paso de build ([arquitectura.md](arquitectura.md#interfaz), [diseno.md](diseno.md)).

## Verificaciones (20/11/2026)

| Comprobación | Resultado |
|---|---|
| `python manage.py test --settings=config.settings_test` | 182 pruebas, 181 correctas. Falla `EntregasFallidasTests.test_confirma_por_post_con_actor_fecha_mensaje_y_estado_fallido`: espera el texto "Cronología HU 34", que la plantilla dejó de mostrar antes del rediseño. Hay que ajustar el test o la plantilla. |
| `python manage.py check` | Sin problemas. |
| `python manage.py makemigrations --check --dry-run` | Sin migraciones pendientes. |
| Carga de `demo/datos-demo.json` sobre una base en memoria | Correcta (13 pedidos). |
| `python3 scripts/check_docs.py .` | Enlaces locales correctos. |

La conexión real a Neon no forma parte de la suite.

## Limitaciones conocidas

- Configuración de desarrollo: `DEBUG` activo, sin HTTPS y sin límite de intentos en el ingreso por PIN.
- Sin notificación activa al operario cuando un repartidor rechaza o deja vencer una asignación (parte del criterio de la HU 18).
- Si un evento referencia una fotografía cuyo archivo no existe, el endpoint de evidencia responde 500 en lugar de 404.
- La contraseña `operario` que se documentaba para el usuario `admin` de los datos de demostración no coincide con su hash ([demo/README.md](../demo/README.md)).
- `django-crispy-forms` y `crispy-bootstrap5` siguen instalados, pero ninguna plantilla los usa.
- El historial general de pedidos no tiene paginación.
- No hay licencia declarada ni CI.
