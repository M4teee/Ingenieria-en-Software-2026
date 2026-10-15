# Índice de documentación

Leé primero el estado para conocer qué existe en el código y qué sigue pendiente. Este material orienta el trabajo, pero no reemplaza las fuentes originales ni la inspección del repositorio.

## Documentos

- [`PROJECT_BRIEF.md`](PROJECT_BRIEF.md): propósito, alcance y requisitos extraídos de las fuentes.
- [`SOURCE_INDEX.md`](SOURCE_INDEX.md): ubicación y utilidad de las fuentes académicas originales.
- [`context/README.md`](context/README.md): política de privacidad, procedencia y regeneración de la exportación Taiga derivada.
- [`CURRENT_STATE.md`](CURRENT_STATE.md): implementación observada, verificaciones y pendientes.
- [`DECISIONS.md`](DECISIONS.md): decisiones técnicas registradas y temas sin resolver.
- [`KNOWLEDGE_BASE.md`](KNOWLEDGE_BASE.md): resumen de contexto y discrepancias entre fuentes.
- [`TASK_TEMPLATE.md`](TASK_TEMPLATE.md): guía para describir una tarea y sus criterios de aceptación.
- [`DOCUMENTATION_WORKFLOW.md`](DOCUMENTATION_WORKFLOW.md): revisión posterior a `git pull` y previa a `git push`.
- [`../scripts/check_docs.py`](../scripts/check_docs.py): comprobación mecánica local de enlaces y rutas.

## Mantenimiento

- Las fuentes originales prevalecen sobre los resúmenes. Indicá si cada dato es requisito, decisión, interpretación o pendiente.
- Al cambiar código o configuración, contrastá el diff con el estado y actualizá `CURRENT_STATE.md` si la implementación cambió.
- Registrá en `DECISIONS.md` solo acuerdos confirmados; conservá las alternativas abiertas como pendientes.
- Las copias portables de las fuentes están en `context/`; consultá su índice y verificá autorización antes de compartirlas fuera del equipo.
- Al añadir o reemplazar una fuente, actualizá `SOURCE_INDEX.md` y `context/README.md` si cambia la procedencia o el tratamiento de privacidad.
- Anotá únicamente verificaciones ejecutadas y el entorno en que se hicieron.
- Seguí `DOCUMENTATION_WORKFLOW.md`; el script solo comprueba enlaces, no la exactitud académica o funcional.
