# Instrucciones para asistentes de código

Antes de trabajar, leé `docs/INDEX.md` y los documentos pertinentes. Comprobá el estado actual del repositorio; las síntesis pueden quedar desactualizadas.

## Fuentes y requisitos

- Las consignas, entrevistas y documentos listados en `docs/SOURCE_INDEX.md` son referencias para los requisitos. Las copias versionadas están en `docs/context/`; verificá su alcance y autorización antes de compartirlas fuera del equipo.
- Separá requisitos explícitos, acuerdos registrados, interpretación y preguntas abiertas. No conviertas una propuesta del PGP, una historia o una alternativa técnica en una funcionalidad ya implementada o una decisión aprobada.
- Ante contradicciones entre fuentes, código y documentación, describí la discrepancia y conservá el comportamiento existente hasta que el equipo decida.

## Cambios y verificación

- Preservá el código existente. Modificá únicamente lo que pida la tarea y no hagas refactors, renombres o reformatos ajenos a su alcance.
- Antes de editar, inspeccioná los archivos relevantes y los cambios locales. No descartes trabajo ni alteres el historial de Git.
- Después de `git pull` y antes de preparar cambios para `git push`, seguí `docs/DOCUMENTATION_WORKFLOW.md`. Actualizá `docs/CURRENT_STATE.md` y solo los otros documentos afectados; no atribuyas cambios recibidos a quien hizo el pull.
- Leé `docs/INDEX.md` para ubicar contexto y consultá en `docs/SOURCE_INDEX.md` las fuentes originales pertinentes. Los Markdown son síntesis derivadas, no fuentes primarias.
- Usá `python3 scripts/check_docs.py .` para revisar enlaces locales y rutas específicas de una máquina; esta verificación no reemplaza la revisión semántica ni de privacidad.
- Ejecutá verificaciones pertinentes y reportá los comandos y resultados reales. No afirmes que una prueba o funcionalidad funciona si no la ejecutaste.
- No publiques, hagas push ni despliegues sin una instrucción explícita.

No registres secretos, datos personales innecesarios ni contenido confidencial. La configuración Django actual es de desarrollo; no la trates como apta para producción.
