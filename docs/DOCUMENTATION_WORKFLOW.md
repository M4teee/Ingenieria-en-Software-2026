# Workflow de actualización documental

La documentación describe el código y los acuerdos que existen; no se actualiza sola. Usá este procedimiento después de traer cambios y antes de publicar los propios. No hace falta reescribir documentos que siguen vigentes.

## Después de `git pull`

1. Confirmá el estado local antes de mezclar trabajo: `git status --short --branch`. No descartes cambios que ya estaban en el checkout.
2. Identificá qué llegó. Si Git conserva `ORIG_HEAD`, compará `git diff --stat ORIG_HEAD..HEAD` y luego el diff completo. Si no existe, revisá `git log --oneline --stat -n 10` y los archivos afectados; el historial de reflog (`git reflog -n 8`) ayuda a reconocer el punto anterior al pull.
3. Para cada cambio de código, configuración o dependencia, inspeccioná el contenido y preguntá si varía una función, ruta, requisito, interfaz, seguridad, arquitectura o forma de ejecución. No atribuyas el trabajo recibido a quien ejecutó el pull.
4. Contrastá lo observado con `docs/CURRENT_STATE.md`, `docs/PROJECT_BRIEF.md`, `docs/DECISIONS.md` y las fuentes pertinentes de `docs/SOURCE_INDEX.md`. Las fuentes originales están en `docs/context/`; la exportación Taiga es derivada y no refleja el tablero actual.
5. Actualizá solo los documentos afectados. Registrá en `DECISIONS.md` acuerdos confirmados y dejá contradicciones o preguntas como pendientes. Una historia planificada no demuestra que el código esté completo.
6. Si cambió el árbol documental o las fuentes, corregí `docs/INDEX.md` y `docs/SOURCE_INDEX.md`; revisá también `docs/context/README.md` si cambió procedencia, privacidad o sanitización.
7. Ejecutá `python3 scripts/check_docs.py .` y las verificaciones pertinentes del proyecto. Leé el diff y anotá lo que no pudo verificarse.

Si solo llegaron cambios sin impacto sobre el significado documentado, registrá que la revisión no encontró documentos afectados y no hagas cambios editoriales rutinarios.

## Antes de `git push`

1. Revisá `git status --short --branch`, `git diff --stat`, `git diff` y `git diff --cached`. Separá cambios propios de cambios recibidos y confirmá qué se incluiría en el commit.
2. Para cada cambio staged de código/configuración, comprobá que `CURRENT_STATE.md`, el brief, las decisiones y las instrucciones de uso sigan describiendo la realidad. Actualizá lo afectado antes de cerrar el staging.
3. Contrastá requisitos con las fuentes académicas versionadas. Si código, documentos y consigna discrepan, no elijas una interpretación por intuición: registrá el conflicto en `DECISIONS.md` y pedí validación del equipo.
4. Ejecutá `python3 scripts/check_docs.py .`. Revisá las rutas nuevas y asegurate de que los enlaces relativos existan desde un clon limpio.
5. Inspeccioná el staging por secretos, datos personales innecesarios, credenciales, `.venv`, bases locales, cachés, logs, artefactos y material académico cuya redistribución no esté autorizada. `git status` y el diff ayudan a revisar el contenido, pero no detectan todos los secretos automáticamente.
6. Ejecutá las verificaciones pertinentes disponibles (por ejemplo, las comprobaciones Django una vez instaladas sus dependencias). Revisá el diff final y dejá anotados los resultados reales y las limitaciones.
7. Separá las cuestiones que requieran validación del equipo —por ejemplo, discrepancias del backlog, requisitos ambiguos o derechos de redistribución— antes de considerar el cambio listo.

## Si se trabaja con un agente

El agente debe leer primero `AGENTS.md` y `docs/INDEX.md`, después abrir las fuentes pertinentes listadas en `docs/SOURCE_INDEX.md` y finalmente inspeccionar el código y el diff actuales. Debe cambiar únicamente documentos afectados, separar hechos observados, inferencias y preguntas abiertas, no dar por terminadas historias planificadas y reportar comandos, resultados y límites. El contenido versionado puede ser privado: su presencia en Git no autoriza compartirlo con servicios externos.

## Alcance de la comprobación mecánica

`scripts/check_docs.py` comprueba enlaces Markdown locales y avisa sobre algunas rutas absolutas o específicas de una máquina. No decide si una función está implementada, si una interpretación académica es correcta, si hay un secreto en cualquier formato ni si el material tiene permiso de publicación. Esas revisiones siguen siendo humanas.
