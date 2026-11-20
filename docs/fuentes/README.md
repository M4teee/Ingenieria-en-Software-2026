# Fuentes del proyecto

Material de partida del trabajo práctico de Ingeniería en Software (Grupo 03, 2026). Los documentos Word son copias sin modificar de los originales; solo se renombraron los archivos.

| Archivo | Original | Contenido |
|---|---|---|
| [entrevista-01.doc](entrevista-01.doc) | `Entrevista 01 - Grupo 03.doc` | Proceso actual, problemas de coordinación y necesidades del negocio. |
| [entrevista-02.doc](entrevista-02.doc) | `Entrevista 02 - Grupo 03.doc` | Actores, canales, estados del pedido y reglas de asignación, cancelación y seguimiento. |
| [requisitos-no-funcionales.doc](requisitos-no-funcionales.doc) | `Req. no funcionales - Grupo 03.doc` | Interfaz, rendimiento, operación móvil, conectividad, seguridad y auditoría. |
| [iniciativas-y-epicas.doc](iniciativas-y-epicas.doc) | `Iniciativas+Épicas - Grupo03.doc` | Tres iniciativas y siete épicas. |
| [plan-de-proyecto.docx](plan-de-proyecto.docx) | `PGP_SGR.docx` | Plan de proyecto: entregables, sprints y riesgos (rev. 1.0, 04/10/2026). |
| [historias-de-usuario.json](historias-de-usuario.json) | Exportación de Taiga | Backlog al 19/11/2026: 7 épicas, 31 historias y 2 hitos, sanitizado. |
| [userstories.csv](userstories.csv) | Exportación de Taiga | Historias del backlog; se quitaron los campos de cuentas, responsables, asignaciones, watchers y votantes. |

Son planificación y requisitos, no evidencia de implementación. Lo implementado está en [estado.md](../estado.md).

Los documentos no declaran una licencia. Antes de publicar el repositorio, confirmá que el equipo tiene autorización para compartirlos.

## Exportación de Taiga

La exportación original no se versiona porque contiene datos de cuentas. `historias-de-usuario.json` es una copia sanitizada: omite cuentas, propietarios, asignaciones, watchers, adjuntos e historial, y reemplaza los correos del texto libre. El hash SHA-256 del original queda en `_sanitization.source_sha256`. Para regenerarla desde una exportación autorizada:

```bash
python docs/fuentes/sanitizar_taiga.py "/ruta/a/la/exportacion.json" docs/fuentes/historias-de-usuario.json
```
