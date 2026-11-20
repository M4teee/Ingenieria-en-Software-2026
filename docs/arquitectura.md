# Arquitectura

Monolito Django con una aplicación por responsabilidad y una interfaz renderizada en el servidor.

## Aplicaciones

| Aplicación | Responsabilidad | Archivos clave |
|---|---|---|
| `main.homePage` | Entrada pública, redirección de cada sesión a su panel y etiquetas de presentación | `views.py`, `templatetags/sgr_ui.py` |
| `main.operario` | Comercios, alta y detalle de pedidos, asignación, repartidores, entregas fallidas y devoluciones | `models.py` (`Comercio`, `Devolucion`), `forms.py`, `views.py` |
| `main.repartidor` | Pedido, historial de estados, perfil del repartidor, ingreso por PIN, cambios de estado y evidencia | `models.py` (`Pedido`, `HistorialEstado`, `Repartidor`), `forms.py`, `views.py` |
| `main.clienteFinal` | Seguimiento público de solo lectura | `views.py` |
| `main.users` | Usuario con el rol `is_operario` y backend de autenticación cacheado | `models.py`, `backends.py` |
| `main/despacho.py` | Asignación automática FIFO, liberación y vencimiento de asignaciones | — |
| `config` | Ajustes (`settings.py`, `settings_test.py`), pool de PostgreSQL (`pool.py`) y URLs | — |

## Modelo de datos

- `Comercio`: nombre único, dirección, contacto y `activo`.
- `Pedido`: código público aleatorio y único, clave de idempotencia, comercio, datos de destino y paquete, vehículo requerido, hora estimada, estado, repartidor (`User`) y marcas de asignación y aceptación. Las transiciones válidas están en `Pedido.TRANSICIONES_PERMITIDAS`.
- `HistorialEstado`: cada cambio de estado con usuario, fecha, incidencia y fotografía opcional.
- `Repartidor`: perfil uno a uno con `User`, PIN, DNI, vehículo y disponibilidad (`disponible`, `disponible_desde`).
- `Devolucion`: confirmación inmutable de la devolución de un pedido fallido.

## Recorrido de un pedido

1. El operario carga el pedido (`PedidoForm`). En una transacción se valida el comercio activo, se genera el código con `secrets`, se crea el evento inicial y se intenta el despacho. La clave de idempotencia evita duplicados al reenviar el formulario.
2. `despacho_automatico` elige al repartidor activo y disponible con el mismo vehículo que espera hace más tiempo. Si no hay candidato, el pedido queda `registrado` y el panel muestra la alerta con **Reintentar asignación**. El operario también puede asignar a mano.
3. El repartidor ve la asignación y tiene 5 minutos para aceptarla. Si la rechaza o vence, el pedido se libera y se reintenta el despacho.
4. El repartidor avanza `asignado → retirado → en_viaje → entregado | fallido`. Cada cambio crea un `HistorialEstado`. La foto opcional (Retirado, Entregado, Fallido) se valida y comprime antes de guardarse, y la escritura es atómica.
5. El cliente consulta el estado con el código. La evidencia se sirve por un endpoint protegido: operario, staff o el repartidor asignado.

## Accesos

| Rol | Condición | Rutas |
|---|---|---|
| Público | — | `/`, `/clienteFinal/` |
| Operario | `is_operario` (independiente de `is_staff`) | `/operario/` |
| Repartidor | perfil `Repartidor` con usuario activo | `/repartidor/` |
| Administrador | `is_staff` y permisos de modelo | `/admin/` |

Una sesión activa que abre `/` se redirige a su panel.

## Interfaz

Plantillas Django sin aplicación frontend separada ni paso de build.

```
Backend/templates/
├── base.html              Fuentes, estilos, mensajes y scripts
├── layouts/               operario (menú lateral), repartidor, publico, acceso
├── components/            marca, menú, estado, recorrido, campo, resumen de errores, mensajes
└── <aplicación>/          Una plantilla por pantalla
Backend/static/
├── sgr/                   sgr.css (tokens y componentes), sgr.js, icons.svg (Lucide)
├── vendor/basecoat/       Basecoat UI 1.1.0 precompilado (MIT)
├── js/                    Interruptores de comercios y repartidores
└── css/                   Solo para Django Admin
```

- Basecoat aporta botones (`data-variant`, `data-size`), campos `.field`, diálogos `<dialog class="dialog">` e interruptores `role="switch"`. `sgr.css` remapea sus tokens a la paleta propia y agrega el resto ([diseno.md](diseno.md)).
- Los resets propios van en `@layer base`; los componentes propios, sin capa, para poder refinar los de Basecoat.
- Las actualizaciones en vivo (panel cada 5 s, disponibilidad de repartidores, cuenta regresiva) son JavaScript sin dependencias.

### Marcado del que dependen los tests

Varios tests verifican HTML literal. Al editar plantillas, conservá:

- `<dd class="col-sm-8">Sin asignar</dd>` en el detalle del pedido.
- `class="img-thumbnail"`, `data-bs-toggle="modal"`, `data-bs-target="#modalEvidencia"` e `id="modalEvidencia"` (ahora `sgr.js` abre un `<dialog>` nativo leyendo esos atributos).
- `id="alerta-sin-repartidor"` con las clases `position-fixed top-0 end-0`.
- El orden de atributos `type="checkbox" role="switch" data-nombre=…` o `data-username=…`.
- `onsubmit="return confirm(` en la cancelación, `<output` en el PIN regenerado, `data-filtro-estado` e `id="mensaje-estado-comercio"`.
- "Cargar pedido" aparece una sola vez en el panel del operario; el panel del repartidor no enlaza a `/operario/`, `/admin/` ni `/clienteFinal/`.
