# Sistema de Gestión de Repartos

Aplicación web para registrar pedidos de comercios, coordinar su entrega y ofrecer seguimiento de su estado.

## Objetivo

El sistema centraliza la información de los pedidos desde su registro hasta el cierre de la entrega. Permite al personal operativo gestionar pedidos y asignaciones, a los repartidores atender entregas y a los clientes consultar su evolución mediante un código de seguimiento.

## Funcionalidades disponibles

- Alta de pedidos asociados a comercios activos, con código de seguimiento, estado inicial e historial.
- Panel del operario para revisar pedidos activos, consultar el detalle, usar asignación automática FIFO o seleccionar manualmente un repartidor compatible y reintentar asignaciones pendientes.
- Gestión de comercios y repartidores, con edición, activación/desactivación y regeneración manual del PIN.
- Seguimiento de pedidos fallidos y registro de su devolución.
- Módulo autenticado del repartidor para responder a asignaciones, actualizar estados y registrar fotografías de retiro, entrega o incidencia.
- Consulta pública de estado e historial mediante el código del pedido.
- Administración de comercios, usuarios y perfiles de repartidor mediante Django Admin.

## Entrada y navegación por rol

- `/` es la entrada pública de seguimiento; también está disponible en `/clienteFinal/`. No requiere cuenta.
- Las personas operarias ingresan desde **Iniciar sesión como operario** y, tras autenticar una cuenta activa con `is_operario`, continúan en `/operario/`.
- Las personas repartidoras ingresan con su PIN desde **Iniciar sesión como repartidor** y continúan en `/repartidor/`.
- Las sesiones activas que vuelven a `/` se redirigen al panel correspondiente. La navegación oculta los accesos de los otros roles.
- Django Admin está en `/admin/`; Django exige una cuenta activa con `is_staff` y los permisos del modelo. El enlace aparece en la experiencia del operario.

El backlog versionado del 19/11/2026 contiene 31 historias; todas figuran como “Done” en esa exportación, pero el estado de Taiga en vivo no fue consultado. La asignación automática FIFO corresponde a HU 41 y el reintento a HU 42; HU 22 trata los datos visibles durante la asignación. El sistema no calcula cercanía geográfica y HU 18 todavía no envía una notificación activa al operario ante un rechazo. El estado probado y las limitaciones se mantienen en [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) y en el [informe de auditoría pre-demo](docs/INFORME-AUDITORIA-PRE-DEMO-2026-11-19.md).

## Usuarios e interfaces

| Usuario | Responsabilidad | Interfaz |
|---|---|---|
| Cliente final | Consultar estado e historial con el código de seguimiento, sin cuenta | `/` o `/clienteFinal/` |
| Operario (`is_operario`) | Registrar, revisar y asignar pedidos | `/operario/` |
| Repartidor con perfil activo | Responder asignaciones, actualizar estados y consultar sus pedidos e historial | `/repartidor/` |
| Administrador de Django (`is_staff`) | Administrar usuarios y datos con permisos de modelo | `/admin/` |

## Tecnologías y arquitectura

- Python 3.14 y Django 6.1.
- SQLite para desarrollo local; PostgreSQL/Neon si se configura `DATABASE_URL` con un URL `postgres://` o `postgresql://`.
- Plantillas Django para las interfaces web; `Frontend/` no contiene una aplicación frontend independiente.
- Pillow para validar y procesar fotografías.
- Aplicaciones Django separadas por responsabilidad: `operario`, `repartidor`, `clienteFinal`, `homePage` y `users`.

## Estado del proyecto

El repositorio incluye flujos para registro, despacho automático FIFO, alternativa manual, operación del repartidor y seguimiento público. La configuración Django es de desarrollo y no está preparada para producción. El PIN se almacena como texto numérico para que el operario pueda comunicar el nuevo PIN (decisión registrada); el login por PIN no tiene limitación de intentos. La guía describe SQLite y Neon, aunque Neon no se pudo probar en esta auditoría por falta de credenciales locales.

## Documentación

- [Estado actual y limitaciones](docs/CURRENT_STATE.md)
- [Guía de instalación, ejecución y pruebas](docs/GUIA-EJECUCION-Y-PRUEBAS.md)
- [Manual de uso por rol](docs/MANUAL-DE-USO.md)
- [Tour técnico de la aplicación](docs/TOUR-APLICACION.md)
- [Requisitos y fuentes](docs/PROJECT_BRIEF.md) · [Índice de fuentes](docs/SOURCE_INDEX.md)
- [Índice completo de documentación](docs/INDEX.md)
- [Informe de auditoría pre-demo](docs/INFORME-AUDITORIA-PRE-DEMO-2026-11-19.md)
