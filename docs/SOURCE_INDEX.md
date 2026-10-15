# Índice de fuentes académicas

Las rutas canónicas siguientes son relativas al repositorio y funcionan desde cualquier clon. Las fuentes originales prevalecen sobre esta síntesis; la exportación Taiga incluida es una derivación sanitizada, no el archivo privado completo.

| Nombre original | Copia versionada | Formato y tipo | Utilidad y alcance | Límites conocidos |
|---|---|---|---|---|
| `Entrevista 01 - Grupo 03.doc` | [`docs/context/Entrevista 01 - Grupo 03.doc`](context/Entrevista%2001%20-%20Grupo%2003.doc) | DOC; original copiado byte por byte | Releva el proceso actual, los problemas de coordinación y las necesidades iniciales. | Entrevista fechada el 04/09/2026; no equivale a una especificación aprobada. |
| `Entrevista 02 - Grupo 03.doc` | [`docs/context/Entrevista 02 - Grupo 03.doc`](context/Entrevista%2002%20-%20Grupo%2003.doc) | DOC; original copiado byte por byte | Aporta actores, canales, estados y reglas de asignación, cancelación y seguimiento. | Entrevista fechada el 11/09/2026; contrastar interpretaciones con el equipo. |
| `Req. no funcionales - Grupo 03.doc` | [`docs/context/Req. no funcionales - Grupo 03.doc`](context/Req.%20no%20funcionales%20-%20Grupo%2003.doc) | DOC; original copiado byte por byte | Requisitos de interfaz, rendimiento, operación móvil, conectividad, seguridad y auditoría. | Documento de septiembre de 2026; el repositorio no demuestra que esos requisitos estén implementados. |
| `Iniciativas+Épicas - Grupo03.doc` | [`docs/context/Iniciativas+Épicas - Grupo03.doc`](context/Iniciativas%2B%C3%89picas%20-%20Grupo03.doc) | DOC; original copiado byte por byte | Describe tres iniciativas y siete épicas del SGR. | Documento de septiembre de 2026; planificación, no evidencia de avance. |
| `PGP_SGR.docx` | [`docs/context/PGP_SGR.docx`](context/PGP_SGR.docx) | DOCX; original copiado byte por byte | Plan de proyecto, entregables, fechas, sprints y riesgos previstos. | Revisión 1.0, 04/10/2026; el calendario no confirma progreso ni vigencia actual. |
| `Historias de Usuario.json` | [`docs/context/Historias de Usuario.sanitized.json`](context/Historias%20de%20Usuario.sanitized.json) | JSON; exportación Taiga derivada y sanitizada | Snapshot del backlog disponible: 7 épicas, 28 historias y 2 hitos. Permite consultar descripciones, estados y planificación registrados en esa exportación. | El JSON original marcaba el proyecto como privado e incluía 318 eventos con identidades de cuenta. La copia omite cuentas, propietarios, asignaciones, watchers, adjuntos, notas de bloqueo e historial/actividad; los correos en texto libre se reemplazan. No representa Taiga en vivo. La nota previa de 29 historias no coincide y la diferencia sigue sin explicación. |

Los cinco documentos Word se preservaron como archivos originales. No se encontró en el contenido inspeccionado una prohibición expresa de redistribución; tampoco incluyen una licencia explícita. Antes de hacer público el repositorio, el equipo debe confirmar que tiene autorización para compartirlos. El PGP cita IEEE Std 1058, pero no incluye una copia de esa norma.

La procedencia, la política de sanitización y el modo de regenerar el derivado se explican en [`docs/context/README.md`](context/README.md). No hace falta acceso a la carpeta Downloads para leer las fuentes versionadas.

## Fuentes no incluidas

- No se encontró la consigna general de la materia ni presentaciones de cátedra.
- No se incluyó un enlace o acceso a Taiga en vivo; no se consultó el servicio.
- Las entrevistas, el plan y las historias no sustituyen una especificación funcional aprobada si el equipo dispone de una aparte.
