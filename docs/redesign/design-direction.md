# Dirección de diseño: "Cuadrícula"

Estado: implementada en las plantillas de `Backend/templates/` y en `Backend/static/sgr/`.

## Idea central

SGR coordina repartos en La Plata (los datos de demo usan el prefijo 221 y direcciones como "Diagonal 74"). La ciudad es conocida por su trazado: una cuadrícula atravesada por diagonales. Esa imagen es la única licencia decorativa del sistema:

- **Marca:** un cuadrado amarillo señal con dos calles en cuadrícula y una diagonal que termina en un punto de destino (`templates/components/marca.html`, `static/sgr/favicon.svg`).
- **Trama:** el mismo trazado, en líneas al 5–7 % de opacidad, sobre la tinta "noche" del rail del operario, la barra del repartidor, la cabecera pública y el panel lateral de los accesos (`.trama`).

Todo lo demás es silencioso: superficies blancas sobre un fondo tiza frío, tipografía con carácter y color reservado para el estado de los pedidos. 

## Paleta (tokens en `Backend/static/sgr/sgr.css`)

| Token | Hex | Uso |
|---|---|---|
| `--sgr-noche` | `#172033` | Tinta del texto, navegación, botón primario |
| `--sgr-tiza` | `#EEF1F4` | Fondo de trabajo (frío, no crema) |
| `--sgr-papel` | `#FFFFFF` | Superficies |
| `--sgr-linea` | `#DCE1E8` | Bordes y divisores |
| `--sgr-tenue` | `#5C6880` | Texto secundario (5,6:1 sobre blanco) |
| `--sgr-senal` | `#F2B705` | Acción principal única de cada pantalla, paso actual, marca |
| `--sgr-cobalto` | `#2448C8` | Foco visible |

**Estados del pedido** (texto/fondo; siempre con ícono + texto, nunca solo color — WCAG 1.4.1): registrado gris pizarra, asignado violeta, retirado verde azulado, en viaje azul, entregado verde, fallido rojo, cancelado gris; "atención" (sin repartidor) ámbar. Las asignaciones de color siguen la convención observada en Onfleet.

La señal amarilla lleva texto noche (≈9:1). Se usa en: "Cargar pedido", "Consultar pedido", "Aceptar pedido", el siguiente paso del repartidor, "Registrar pedido", "Ingresar" (PIN). Las demás acciones son primarias en noche o contorno.

## Tipografía

- **Archivo** (variable, ejes `wdth` 62–125 y `wght`): una sola familia con contraste de **ancho**, no de familias. Titulares a `wdth 125`/`760` (`.display`), títulos de pantalla a `wdth 112`/`700` (`.titulo`), cuerpo a `wdth 100`/`400`, 15 px, interlineado 1,5. El ancho expandido evoca la señalética de transporte sin recurrir a un estilo de cartel.
- **IBM Plex Mono 500** solo para **códigos de seguimiento** (datos que el usuario copia y dicta, donde 0/O y 1/I deben distinguirse). No se usa mono para rótulos.
- Cifras con `font-variant-numeric: tabular-nums` (fechas, cuenta regresiva, contadores).
- Rótulos en mayúscula inicial; sin versalitas ni "eyebrows" en mayúsculas.

## Composición por flujo (no una plantilla para todo)

| Flujo | Composición |
|---|---|
| Operario, tablero | Rail noche + barra con búsqueda global y la acción "Cargar pedido". Encima de la tabla, una fila de **chips de estado** (Registrados, Asignados, Retirados, En viaje) con sus conteos reales, que filtran la tabla. Franja ámbar "Pedido sin repartidor disponible" solo cuando corresponde. Indicador "Actualizado hace N s". |
| Operario, detalle | Cabecera con código y **recorrido** (stepper); a la izquierda datos y cronología con evidencia; a la derecha un panel de acción (asignar / cancelar / ir a fallidos) que se fija al hacer scroll. |
| Operario, formularios | Secciones con explicación a la izquierda y campos a la derecha; resumen de errores enfocado al inicio; pie de acciones fijo. |
| Operario, fallidos | Lista de **casos** (no tabla): motivo como cita, foto, cronología de devolución y la acción. |
| Repartidor | Columna única de teléfono. Interruptor grande de disponibilidad cuando no hay pedido (con pedido activo se reduce a una línea), **ficha de ruta** A → B con línea discontinua, una sola acción siguiente con foto opcional, fija al pie de la pantalla en teléfonos; "No se pudo entregar" separado en un desplegable rojo. Asignación pendiente con reloj grande `m:ss` y barra de tiempo. |
| Público | Cabecera noche con trama; titular expandido "Tu envío, en cada etapa."; el estado consultado es el titular de la página; recorrido de etapas y cronología con lo más reciente primero. |
| Accesos | Pantalla dividida: panel noche con trama y propósito, formulario en blanco. El PIN tiene visor de 4 casillas y teclado numérico táctil (en pantallas táctiles). |

## Superficies, radios y profundidad

- Radios jerárquicos: controles 8 px, paneles 14 px, fichas del repartidor 20 px, estados en píldora.
- Sombras casi nulas en superficies (`--sombra-panel`); sombras marcadas solo en lo que flota (diálogos, mensajes, aviso flotante).
- Bordes de 1 px para estructura; acento de color en el borde superior o izquierdo solo cuando codifica algo (panel de acción, caso pendiente, fila que requiere atención).

## Movimiento

- Una sola animación no solicitada: el pulso del indicador "en vivo" (se detiene con `prefers-reduced-motion`).
- Movimiento como respuesta: entrada de mensajes (320 ms, `cubic-bezier(.2,.8,.2,1)`), cajón móvil, interruptor, spinner en botones ocupados, barra de tiempo de la oferta.
- Solo `transform`/`opacity`/colores; nada de `transition: all`. `prefers-reduced-motion: reduce` anula animaciones.

## Decisiones y alternativas descartadas

1. **Crema + serif + acento terracota** — descartada: es una estética genérica que no surge del producto.
2. **Fondo casi negro con un acento ácido** — descartada por el mismo motivo y por legibilidad al aire libre del repartidor.
3. **Estética de periódico (filetes, radio cero, columnas densas)** — descartada por genérica y por su densidad poco apta para el teléfono del repartidor.
4. **Kit SaaS de tarjetas KPI** — descartado: no hay métricas reales más allá de los conteos por estado; esos conteos se muestran como chips que además filtran.
5. **Verde de la marca anterior como primario** — descartado: choca con el verde semántico de "Entregado".
6. **Mapa o seguimiento en vivo** — no existe en el producto; no se simula.

## Referencias

Guías de accesibilidad WCAG 2.2 AA, Nielsen Norman Group, GOV.UK Design System y productos de despacho y seguimiento (Onfleet, Shopify, Aftership). Las referencias de producto se usaron como patrones (estado con ícono, primero lo que requiere acción, un paso por vez para el repartidor), no como identidad visual.
