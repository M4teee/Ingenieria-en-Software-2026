# Arquitectura del frontend

## Decisión

**Plantillas Django (sin cambio de arquitectura) + Basecoat UI 1.1.0 precompilado (vendorizado) + capa propia de CSS con tokens + JavaScript vanilla.** Sin paso de build, sin Node, sin SPA.

## Alternativas evaluadas

| Criterio | A. Django templates + CSS/componentes | B. Django API + React | C. Django + HTMX/Alpine |
|---|---|---|---|
| Capacidad visual | Completa (todo es CSS) | Completa | Completa |
| Integración | Directa: vistas, formularios, mensajes y CSRF ya existen | Requiere API REST para ~20 vistas, serialización, rutas cliente | Media: atributos nuevos en vistas y fragmentos parciales |
| Autenticación / permisos | Sin cambios (`login_required`, `is_operario`, PIN) | Hay que exponerlos vía API y duplicar chequeos | Sin cambios |
| CSRF / formularios | Nativo (`{% csrf_token %}`, validación de `forms.Form`) | Token por header, validación duplicada en cliente | Nativo |
| Tests existentes (182, muchos verifican HTML) | Se conservan | Se rompen en su mayoría | Se conservan con ajustes |
| Rendimiento | HTML del servidor, ~20 KB de JS propio | Bundle + hidratación | Bueno |
| Mantenimiento por el equipo (curso de Ingeniería de Software) | Mismo stack que ya conocen | Stack nuevo | Dos librerías nuevas |
| Despliegue | Igual que hoy | Build y hosting de estáticos | Igual |

Se eligió **A** porque la calidad visual buscada no depende de React y los flujos ya funcionan con formularios del servidor; migrar habría reescrito el backend y descartado la suite de tests. Las interacciones dinámicas que ya existían (sondeo cada 5 s, interruptores con `fetch`, cuenta regresiva) se mantienen en JS vanilla.

## Componentes y por qué Basecoat

Basecoat UI (MIT) ofrece componentes con la anatomía de shadcn/ui para HTML plano, sin React. Se usa su CSS ya compilado (`basecoat.cdn.min.css`), así que el proyecto no necesita Node ni un paso de build. Consecuencias:

- No hay utilidades Tailwind arbitrarias: el layout fino está en `static/sgr/sgr.css`.
- De Basecoat se usan: `.btn` (variantes y tamaños por `data-variant`/`data-size`), `.field` (anatomía label/control/error compatible con la salida de Django), `<dialog class="dialog">` (header/section/footer, cierre, `::backdrop`), interruptor `input[role=switch]`, preflight y tokens shadcn (`--primary`, `--border`, …) que se remapean a la paleta SGR.
- Se agregaron variantes propias (`signal`, `atencion`, `peligro`, tamaño `xl`).

### Cascada

Basecoat declara `@layer theme, base, components, utilities`. Los resets propios van en `@layer base` (si no, un `a { color: inherit }` sin capa le gana a `.btn`). Los componentes SGR van sin capa para refinar a Basecoat.

## Estructura de archivos

```
Backend/templates/
  base.html                     esqueleto: fuentes, CSS, mensajes, scripts
  layouts/operario.html         rail + barra superior + cajón móvil
  layouts/repartidor.html       barra compacta, columna de teléfono
  layouts/publico.html          cabecera con trama + bloques hero/content
  layouts/acceso.html           pantalla dividida para login y PIN
  components/                   marca, rail, estado, recorrido, campo, resumen_errores, mensajes
Backend/static/sgr/
  sgr.css                       tokens + componentes + layouts
  sgr.js                        diálogos, mensajes, envío ocupado, archivo, copiar, PIN
  icons.svg                     sprite Lucide 1.76.0 (ISC), 51 íconos
  favicon.svg
Backend/static/vendor/basecoat/1.1.0/   CSS/JS precompilados + LICENSE.md (MIT)
Backend/main/homePage/templatetags/sgr_ui.py   {% icon %}, pasos_estado, iconos por estado/vehículo, iniciales
```

`static/css/variables.css` y `static/css/admin.css` solo los usa Django Admin, que conserva su estilo propio.

## Piezas de presentación fuera de las plantillas

| Archivo | Cambio | Motivo |
|---|---|---|
| `main/homePage/templatetags/sgr_ui.py` | Filtros y etiquetas de presentación | Íconos y stepper sin lógica en plantillas; no consulta la base |
| `main/operario/forms.py` | `empty_label` del campo comercio en castellano | Django 6.1 muestra por defecto "- Select an option -" |
| `static/js/comercios.js`, `repartidores.js` | Interruptores de activo/inactivo con `fetch` | Piden confirmación antes de desactivar y muestran los errores del servidor en la página |

## Compatibilidad con los tests

Varios tests verifican fragmentos HTML; al editar plantillas hay que conservar: `<dd class="col-sm-8">Sin asignar</dd>`, `class="img-thumbnail"`, `data-bs-target="#modalEvidencia"`/`id="modalEvidencia"` (ahora un `<dialog>` nativo que `sgr.js` abre leyendo `data-bs-*`), `id="alerta-sin-repartidor"` con `position-fixed top-0 end-0` (clases redefinidas en `sgr.css`), el orden de atributos `type="checkbox" role="switch" data-…`, `onsubmit="return confirm(` en cancelar, `<output` del PIN, `data-filtro-estado`, `id="mensaje-estado-comercio"`, y que "Cargar pedido" aparezca una sola vez en el tablero.

## Dependencias externas en tiempo de ejecución

Solo Google Fonts (Archivo, IBM Plex Mono). Basecoat, los íconos y los scripts se sirven desde `Backend/static/`. Si las fuentes no cargan, se usan las del sistema.
