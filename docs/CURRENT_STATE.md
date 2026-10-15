# Estado actual

Actualizado: 2026-10-15. Estado observado en la rama `feature/hu-12-cargar-pedido`; esta página debe contrastarse con Git antes de reutilizarla.

## Implementación observada

- `Backend/` contiene el backend Django; `.python-version` fija Python 3.14 y `requirements.txt` fija Django 6.1.2 y sus dependencias. La configuración local usa SQLite, `USE_TZ=True` y `America/Argentina/Buenos_Aires`; `DEBUG=True` y la clave en settings son solo de desarrollo.
- `main.operario` mantiene los comercios, permite altas desde `/operario/pedidos/nuevo/` y limita la carga y confirmación a usuarios autenticados con `is_staff`. El servidor valida que el comercio siga activo. La confirmación muestra el código y ofrece copiarlo.
- `main.repartidor.Pedido` persiste el comercio, código, dirección, especificaciones, fecha estimada, estado, repartidor opcional y clave de idempotencia. Los campos de alta son opcionales en la base para conservar filas previas; el formulario de altas los exige. La migración `0002` agrega los campos y estados sin eliminar los pedidos anteriores.
- El nuevo pedido queda `registrado`, sin repartidor, con código alfanumérico de 20 caracteres generado con `secrets`; su primera fila `HistorialEstado` se crea en la misma transacción e identifica al operario. Los estados conservan el avance del repartidor y agregan cancelación antes del retiro. El historial ordena por fecha y clave primaria.
- `main.clienteFinal` consulta pedidos e historial persistidos en `/clienteFinal/seguimiento/<codigo>/`. Es una consulta pública GET; muestra estado, comercio, estimación solo durante `en_viaje` y fechas del historial, sin exponer contacto, especificaciones, operador ni fotografías.
- `main.repartidor` conserva la vista autenticada para que el repartidor avance pedidos asignados, adjunte fotos al retirar o entregar y registre incidencias. La escritura del estado y del historial ahora es transaccional. No se encontró una interfaz para que el operario asigne pedidos; el modelo permite la relación, pero el flujo de asignación es trabajo pendiente.
- `main.users` extiende `AbstractUser` y asocia opcionalmente un vehículo. `main.homePage` enruta superusuarios al admin, personal `is_staff` a la carga y otros usuarios a la interfaz del repartidor. `Frontend/front` sigue siendo un marcador de posición; las páginas están en plantillas Django.

## Compatibilidad y límites

- La base `Backend/db.sqlite3` no existía antes de las verificaciones del 2026-10-15. La revisión creó el archivo vacío durante `migrate --check`; luego se aplicaron las migraciones. No había pedidos locales preexistentes que migrar. La migración usa campos opcionales/defaults compatibles con filas antiguas, pero la conservación de datos de una base poblada no se ensayó en este entorno.
- HU 24 y HU 38 estaban representadas por datos simulados antes de este trabajo; ahora consumen el modelo persistido. La confirmación del proyecto describe los requisitos HU 12, HU 24 y HU 38. No se consultó Taiga en vivo.
- La exportación Taiga versionada contiene 28 historias, 7 épicas y 2 hitos; es una derivación privada/sanitizada y no prueba el estado actual del tablero.
- Requisitos de fuentes que exceden esta tarea —historial inmutable, operación sin conexión y preparación para producción— no se implementan aquí. Las imágenes del flujo de repartidor usan Pillow y el almacenamiento configurado por Django.
- `Backend/config/settings.py` referencia `STATICFILES_DIRS = [BASE_DIR / 'static']`; la aplicación incluye estáticos propios y usa CDN externos para Bootstrap, iconos y tipografías en `base.html`.

## Verificaciones ejecutadas

En la instalación `.venv` creada desde cero con Python 3.14.8 y los paquetes de `requirements.txt`:

- `python manage.py check`: aprobado, sin incidencias.
- `python manage.py makemigrations --check --dry-run`: aprobado, no hay cambios de modelo pendientes.
- `python manage.py migrate`: aplicó correctamente la migración de orden `0003` sobre la base local; `migrate --check` confirmó que no quedan migraciones pendientes.
- `python manage.py test`: aprobadas las 30 pruebas del proyecto.
- `python -m pip check`: aprobado; no se detectaron dependencias rotas.
- `python3 scripts/check_docs.py .`: aprobado, 35 enlaces Markdown locales comprobados; `git diff --check` sin errores.
- Inspección visual local: recorrido de inicio de sesión, formulario, alta, confirmación, copiado al portapapeles y consulta pública completado. Los fixtures de navegador fueron retirados al terminar.
- La instalación de dependencias requirió red. El primer intento quedó limitado por DNS del entorno aislado; la repetición autorizada completó la instalación.

Los resultados definitivos y los comandos reproducibles están en [`GUIA-EJECUCION-Y-PRUEBAS.md`](GUIA-EJECUCION-Y-PRUEBAS.md). El recorrido por componentes está en [`TOUR-APLICACION.md`](TOUR-APLICACION.md).

## Pendientes conocidos

- No hay pantalla de asignación de pedidos; solo existe el flujo de avance del repartidor una vez asignado.
- La interacción visual se comprobó en el navegador integrado y el copiado real funcionó; no se validó Windows.
- No se ensayó una migración con pedidos heredados reales ni una instalación Windows.
- Confirmar con el equipo el alcance y prioridad vigentes de las historias en Taiga; no se consultó el tablero en vivo.
- Configurar secretos, hosts, HTTPS, base compartida y almacenamiento antes de cualquier despliegue. Django está configurado para desarrollo.
