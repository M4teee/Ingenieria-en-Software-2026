# Sistema de Gestión de Repartos

Aplicación web para registrar pedidos de comercios, coordinar su entrega y ofrecer seguimiento de su estado.

## Objetivo

El sistema centraliza la información de los pedidos desde su registro hasta el cierre de la entrega. Permite al personal operativo gestionar pedidos y asignaciones, a los repartidores atender entregas y a los clientes consultar su evolución mediante un código de seguimiento.

## Funcionalidades disponibles

- Alta de pedidos asociados a comercios activos, con código de seguimiento, estado inicial e historial.
- Panel del operario para revisar pedidos activos, consultar su detalle y asignar manualmente un repartidor disponible.
- Módulo autenticado del repartidor para responder a asignaciones, actualizar estados y registrar fotografías de retiro, entrega o incidencia.
- Consulta pública de estado e historial mediante el código del pedido.
- Administración de comercios, usuarios y perfiles de repartidor mediante Django Admin.

## Entrada y navegación por rol

- `/` es la entrada pública de seguimiento; también está disponible en `/clienteFinal/`. No requiere cuenta.
- Las personas operarias ingresan desde **Iniciar sesión como operario** y, tras autenticar una cuenta activa con `is_staff`, continúan en `/operario/`.
- Las personas repartidoras ingresan con su PIN desde **Iniciar sesión como repartidor** y continúan en `/repartidor/`.
- Las sesiones activas que vuelven a `/` se redirigen al panel correspondiente. La navegación oculta los accesos de los otros roles.
- Django Admin está en `/admin/`; Django exige una cuenta activa con `is_staff` y los permisos del modelo. El enlace aparece en la experiencia del operario.

La asignación manual es una solución provisional para conectar el registro con la operación web. Las HU 22 y 30 aún no están implementadas y sus criterios de asignación automática por cercanía siguen pendientes; esta rama no las marca como completas. El estado de alcance y las verificaciones se mantienen en [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

## Usuarios e interfaces

| Usuario | Responsabilidad | Interfaz |
|---|---|---|
| Cliente final | Consultar estado e historial con el código de seguimiento, sin cuenta | `/` o `/clienteFinal/` |
| Operario (`is_staff`) | Registrar, revisar y asignar pedidos; abrir Django Admin si tiene permisos | `/operario/` y `/admin/` |
| Repartidor con perfil activo | Responder asignaciones, actualizar estados y consultar sus pedidos e historial | `/repartidor/` |

## Tecnologías y arquitectura

- Python 3.14 y Django 6.1.
- SQLite para desarrollo local.
- Plantillas Django para las interfaces web; `Frontend/` no contiene una aplicación frontend independiente.
- Pillow para validar y procesar fotografías.
- Aplicaciones Django separadas por responsabilidad: `operario`, `repartidor`, `clienteFinal`, `homePage` y `users`.

## Estado del proyecto

El repositorio ofrece un flujo funcional de registro, consulta pública, asignación manual y operación del repartidor. La configuración actual es de desarrollo; no está preparada para producción. La asignación automática, una notificación activa al operario ante rechazos y la cancelación desde la interfaz siguen pendientes.

## Documentación

- [Estado actual y limitaciones](docs/CURRENT_STATE.md)
- [Guía de instalación, ejecución y pruebas](docs/GUIA-EJECUCION-Y-PRUEBAS.md)
- [Manual de uso por rol](docs/MANUAL-DE-USO.md)
- [Tour técnico de la aplicación](docs/TOUR-APLICACION.md)
- [Requisitos y fuentes](docs/PROJECT_BRIEF.md) · [Índice de fuentes](docs/SOURCE_INDEX.md)
- [Índice completo de documentación](docs/INDEX.md)
