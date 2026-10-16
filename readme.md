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

La asignación manual es una solución provisional para conectar el registro con la operación web. Las HU 22 y 30 aún no están implementadas y sus criterios de asignación automática por cercanía siguen pendientes; esta rama no las marca como completas. El estado de alcance y las verificaciones se mantienen en [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md).

## Usuarios e interfaces

| Usuario | Responsabilidad | Interfaz |
|---|---|---|
| Operario (`is_staff`) | Registrar pedidos, consultar su historial y seleccionar un repartidor disponible | Panel de operario |
| Repartidor con perfil activo | Responder asignaciones y actualizar sus pedidos | Módulo del repartidor |
| Cliente | Consultar estado e historial con el código de seguimiento | Consulta pública |
| Administrador | Mantener comercios, usuarios y perfiles | Django Admin |

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
