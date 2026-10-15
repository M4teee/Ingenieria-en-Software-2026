# Estado actual

Actualizado: 2026-10-15. Revisión del árbol, la configuración y los puntos de entrada del código. No se modificó código de la aplicación.

## Implementación observada (hechos del código)

- `Backend/` contiene un proyecto Django 6.1.2. `.python-version` solicita Python 3.14; `requirements.txt` fija Django, `asgiref`, `sqlparse`, `django-crispy-forms`, `crispy-bootstrap5` y Pillow.
- La configuración local usa SQLite, `DEBUG=True` y una clave de desarrollo definida en settings. No es una configuración de producción.
- `main.operario` tiene el modelo `Comercio` y su administración. `main.users` extiende el usuario Django y agrega un vínculo a `Vehiculo`.
- `main.repartidor` tiene modelos persistentes `Pedido` y `HistorialEstado`, con migración inicial. Un pedido se vincula a un repartidor; el estado admite las transiciones `asignado → retirado → en_viaje → entregado/fallido`. La vista autenticada del repartidor permite avanzar esos estados y registra usuario, fecha, incidencia y una fotografía opcional para retiro o entrega. La imagen se reduce y convierte a JPEG en la vista. El modelo no tiene estados `registrado` ni `cancelado`.
- Ese modelo de pedido no está integrado con `Comercio` ni con el seguimiento público. Su campo `codigo` es un valor único, pero no se observó generación del código. La página de seguimiento de `main.clienteFinal` continúa usando `PEDIDOS_SIMULADOS` y sus historiales en memoria; acepta solo los códigos de demostración definidos en la vista.
- No se observó una interfaz para que el operario cree o asigne pedidos: `/operario/` intenta renderizar `hola.html`, que no existe en `Backend/templates/`. El modelo `Pedido` tampoco está registrado en el admin de Django.
- `HistorialEstado` guarda cambios, pero la estructura no garantiza inmutabilidad: el modelo permite modificar registros y define borrado en cascada al eliminar un pedido. No se observó cola local para operar sin conexión.
- `Frontend/front` contiene solo un texto marcador; no hay un frontend separado implementado.
- Hay pruebas para seguimiento público y para transiciones/actualización de estado del repartidor. No se ejecutaron en esta revisión. Los tests de operario, usuario y página inicial son plantillas vacías.

## Requisitos y planificación (fuentes; no implican implementación)

La Entrevista 02 describe acceso del operario desde PC (web o escritorio), del repartidor mediante web orientada a smartphones y del cliente mediante web pública. Esas necesidades no fijan por sí solas una plataforma o arquitectura tecnológica elegida por el equipo; la definición de plataformas objetivo sigue pendiente. La misma entrevista enumera siete estados (`registrado`, `asignado`, `retirado`, `en viaje`, `entregado`, `fallido`, `cancelado`), cancelación antes del retiro, asignación a cargo del operario y códigos públicos no predecibles.

Las fuentes versionadas describen siete épicas para comercios, pedidos, repartidores, despacho, operación móvil, consulta pública y auditoría. Son alcance planificado, no evidencia de funcionalidad terminada. La Entrevista 02 y los requisitos no funcionales piden también historial con trazabilidad/fotos, inmutabilidad del historial y tolerancia a cortes de conectividad. El código revisado no implementa todos esos puntos. El PGP organiza entregas entre el 9 de octubre y el 20 de noviembre de 2026; las fechas describen el plan, no el avance real del equipo.

## Discrepancias y preguntas abiertas

- La Entrevista 02 enumera siete estados para el ciclo de vida completo. La sección de definiciones del PGP lista cuatro estados (`retirado`, `en viaje`, `entregado`, `fallido`), y el modelo persistente implementa cinco. Las fuentes no aclaran si la lista del PGP describe solo la parte operativa del repartidor. Antes de implementar el ciclo completo, el equipo debe confirmar la lista autorizada de estados y transiciones.
- La Entrevista 02 pide códigos de seguimiento no predecibles; el modelo solo almacena un `codigo` y la vista pública usa datos de demostración. No se observó cómo se generarían códigos reales.
- Los requisitos no funcionales piden historial inmutable y funcionamiento ante cortes de conectividad. El modelo permite edición/borrado en cascada y no se observó una cola sin conexión; esos requisitos siguen sin verificarse/implementarse en el código revisado.

La exportación Taiga derivada y versionada contiene 28 historias de usuario, 7 épicas y 2 hitos. Se omitieron las cuentas y la actividad del export privado original; no se consultó Taiga en vivo. Un documento previo de esta carpeta indicaba 29 historias; las fuentes disponibles no permiten explicar la diferencia. Confirmar cantidad y estado con el equipo o el tablero cuando corresponda.

`docs/context/` contiene copias de las cinco fuentes Word y una derivación sanitizada del JSON de Taiga. `docs/SOURCE_INDEX.md` identifica formato, alcance y limitaciones; `docs/DOCUMENTATION_WORKFLOW.md` describe la revisión posterior a pull y previa a push. Estos documentos nuevos no alteran la implementación.

## Verificaciones de esta revisión

- `pwd`, `git rev-parse --show-toplevel` y `git status --short --branch` confirmaron que la revisión se realizó en la raíz del repositorio, en `main`. Al inicio había un archivo no rastreado, `docs/AI_INITIALIZATION_PROMPT.md`; se preservó.
- Se inspeccionaron los manifests, settings, rutas, vistas, modelos, migraciones, plantillas y pruebas pertinentes. Los hechos de implementación de arriba son observaciones estáticas del código; no se ejecutó Django.
- Se consultó la Entrevista 02, los requisitos no funcionales y el PGP originales versionados. Sus requisitos y fechas se reportan como contenido de las fuentes, no como decisiones o avance confirmado.
- Se ejecutó `python3 scripts/check_docs.py .`: OK, 28 enlaces Markdown locales verificados.
- `git diff --check` terminó sin errores.
- No se instalaron dependencias, no se ejecutó la aplicación y no se ejecutaron las pruebas.

## Pendientes

- Confirmar historias y estado real con el tablero Taiga.
- Definir la tecnología/interfaz frontend, la base de datos compartida, las plataformas objetivo y el despliegue; las fuentes expresan necesidades por rol, pero la decisión tecnológica está pendiente.
- Completar la integración de pedidos con comercios, el alta/asignación operativa, el seguimiento público persistente y los estados que correspondan a los requisitos aprobados.
- Resolver la plantilla faltante de la ruta de operario.
- Instalar las dependencias en un entorno de desarrollo del proyecto y ejecutar `manage.py check` y las pruebas existentes.
- Revisar claves, `DEBUG`, hosts, HTTPS y almacenamiento antes de cualquier uso de producción.
