# Estado actual

Actualizado: 2026-10-16. Contrasta el código de la rama de rediseño con la configuración, las pruebas y las fuentes disponibles. No se consultó Taiga en vivo.

## Implementación observada

- `Backend/` contiene el backend Django en Python 3.14; `requirements.txt` fija Django 6.1.2 y las dependencias de formularios e imágenes. SQLite es la base local configurada. `Frontend/` es un marcador, no una aplicación frontend aparte.
- `main.homePage` deriva las visitas anónimas de `/` al formulario público de seguimiento; `/clienteFinal/` mantiene la misma consulta. Las sesiones `is_staff` se dirigen a `/operario/` y las sesiones con perfil activo de repartidor a `/repartidor/`. La navegación compartida muestra accesos de login por rol cuando no hay sesión y opciones del propio rol cuando la hay.
- `main.operario` mantiene comercios y gestiona pedidos desde plantillas Django. El operario registra pedidos asociados a comercios activos; la vista vuelve a validar el comercio durante la escritura. El alta es idempotente por clave de solicitud, genera un código seguro y registra `Registrado` en el historial dentro de una transacción.
- El panel de operario en `/operario/` lista los pedidos no finalizados (`registrado`, `asignado`, `retirado`, `en_viaje`) ordenados por antigüedad, con comercio, destino, estado y repartidor asignado; permite abrir el detalle y asignar manualmente un repartidor disponible a un pedido registrado sin asignar. Un pedido `asignado` que todavía espera la aceptación del repartidor (sin `fecha_hora_aceptacion`) no se incluye en esa lista; aparece recién cuando el repartidor confirma. Estado, asignación e historial se guardan juntos. Una respuesta JSON con el mismo filtro actualiza la lista cada 15 segundos mientras el panel permanece abierto.
- `main.repartidor` conserva el perfil con PIN de cuatro dígitos, disponibilidad, respuesta a la asignación en cinco minutos y transiciones del pedido. El repartidor autenticado ve los pedidos que le pertenecen, consulta detalles e historial, y puede adjuntar una fotografía opcional al retirar, entregar o registrar una falla. Las imágenes se limitan a JPEG, PNG o WebP, máximo 10 MB y una por transición. El acceso a evidencia está restringido al personal del sistema o al repartidor dueño del pedido.
- `main.clienteFinal` ofrece búsqueda pública de solo lectura por código en `/clienteFinal/` y consulta en `/clienteFinal/seguimiento/<codigo>/`. Lee el pedido y el historial persistidos. La página pública no presenta datos de contacto, especificaciones, usuarios internos ni fotografías.
- Django Admin mantiene datos de configuración: usuarios, comercios y perfiles de repartidor. No reemplaza los flujos operativos de las plantillas propias.
- Las plantillas comparten identidad SGR y conservan la paleta verde/menta. La navegación es colapsable en pantallas estrechas; operario y repartidor tienen paneles propios y la vista pública concentra el seguimiento.
- Django Admin conserva la autorización estándar de Django: requiere usuario activo con `is_staff`, y cada operación requiere permisos de modelo. El enlace se muestra solo a usuarios `is_staff`; no se modificó la política ni se otorgaron permisos nuevos.

## Requisitos, acuerdos y discrepancias

- **Requisito de HU 12:** comercio activo, estado inicial Registrado, código no predecible, destino, especificaciones y estimación. La implementación actual los satisface en el flujo web; las pruebas cubren alta, repetición, invalidación del comercio, colisión y permisos.
- **Acuerdo del equipo (2026-10-16):** el operario elige manualmente un repartidor disponible desde la web como solución provisional entre los pedidos registrados y el módulo del repartidor.
- **HU 22/30 no implementadas:** sus criterios originales de asignación automática —incluida la cercanía donde corresponde— siguen pendientes. El flujo manual provisional no satisface ni completa esas historias. El modelo tampoco registra ubicación suficiente para calcular cercanía.
- **HU 18:** el repartidor puede aceptar o rechazar la asignación, y la expiración se procesa al entrar al módulo o responder. No se envía una notificación externa al repartidor ni una notificación activa al operario tras un rechazo; el operario puede observar los cambios en el panel al actualizarse.
- No se encontró interfaz para cancelar un pedido, ni una operación de asignación automática. Tampoco se encontraron campos de dimensión/volumen para seleccionar vehículos por capacidad.
- Las fuentes académicas listadas en `SOURCE_INDEX.md` describen necesidades y alternativas; no convierten por sí solas cada propuesta en una implementación confirmada.

## Datos y compatibilidad

- Los pedidos nuevos se relacionan con `Comercio`; `Pedido.repartidor` es opcional para que un pedido pueda existir antes de su asignación. `HistorialEstado` conserva estado anterior/nuevo, usuario, fecha, incidencia y archivo fotográfico.
- El rediseño no cambió modelos ni datos. La revisión previa ejecutó `makemigrations --check --dry-run` sin detectar cambios de modelo pendientes.
- La base local contiene datos de desarrollo preexistentes. No se alteraron ni usaron como evidencia funcional; la inspección del panel fue de solo lectura. La compatibilidad con una base productiva poblada no se validó.
- `DEBUG=True`, clave de desarrollo, almacenamiento local y servicio `runserver` hacen que esta configuración sea solo de desarrollo.

## Verificaciones de esta revisión

En esta tarea, con Python 3.14.8 y las dependencias de `requirements.txt` desde `Backend/`:

- `../.venv/bin/python manage.py check`: aprobado.
- `../.venv/bin/python manage.py test`: 73 pruebas aprobadas (incluye las nuevas del filtro de aceptación en el panel de operario, agregadas el 2026-10-17).
- `python3 scripts/check_docs.py .` desde la raíz: 42 enlaces locales verificados.
- `git diff --check`: aprobado.
- La revisión previa ejecutó `makemigrations --check --dry-run` sin cambios detectados, `migrate --check` aprobado y `pip check` sin dependencias rotas.
- La suite validó la raíz pública, login y redirecciones por rol, ausencia de enlaces cruzados, entrada única de carga, control de acceso al Admin y rechazo de una mutación sobre pedido de otro repartidor, además de los flujos preexistentes.
- Se inspeccionaron visualmente en el navegador local las vistas públicas y del operario con un viewport estrecho. No se accedió con credenciales a la vista autenticada del repartidor ni se hizo una revisión visual de escritorio amplio; las rutas, el aislamiento y las acciones del repartidor sí están cubiertos por pruebas automatizadas.

## Límites y pendientes

- Confirmar y priorizar con el equipo cómo conciliar asignación manual con los criterios originales de asignación automática de HU 22/30.
- Definir un canal de notificaciones para los criterios de HU 18 que requieren avisar al operario.
- No se validó producción, Windows, migración desde una base poblada, ni almacenamiento remoto de archivos.
- Las versiones de Django/paquetes y el entorno se ejecutaron localmente en Python 3.14. No se declara compatibilidad con otras versiones.
- Consultar el [manual de uso](MANUAL-DE-USO.md), la [guía de ejecución y pruebas](GUIA-EJECUCION-Y-PRUEBAS.md) y el [tour técnico](TOUR-APLICACION.md) para los recorridos.
