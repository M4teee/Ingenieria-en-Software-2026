# Guía de contexto del proyecto

Este directorio mantiene el contexto verificable para que una persona o un asistente pueda retomar el trabajo sin depender del historial de un chat. Leé primero `CURRENT_STATE.md` y seguí los enlaces de esta página según la tarea.

## Lectura inicial

1. `PROJECT_BRIEF.md`: propósito, alcance y organización del proyecto.
2. `SOURCE_INDEX.md`: documentos originales, su ubicación, autoridad y estado de acceso.
3. `CURRENT_STATE.md`: situación observada, cambios recientes y trabajo pendiente.
4. `DECISIONS.md`: acuerdos aprobados y propuestas que todavía requieren decisión.
5. `KNOWLEDGE_BASE.md`: síntesis para orientación, con separación explícita entre confirmado y pendiente.
6. `TASK_TEMPLATE.md`: formato para iniciar una tarea con alcance y criterios claros.

## Qué documento actualizar

| Si cambia… | Actualizá… |
|---|---|
| El propósito, usuarios, alcance o entregables | `PROJECT_BRIEF.md` |
| Una fuente original, su ubicación o versión | `SOURCE_INDEX.md` |
| Un acuerdo del equipo o una propuesta | `DECISIONS.md` |
| El estado del código, tareas, riesgos o verificaciones | `CURRENT_STATE.md` |
| El resumen de conocimientos verificados | `KNOWLEDGE_BASE.md` |
| La definición de una tarea concreta | `TASK_TEMPLATE.md` o la tarea correspondiente |

## Reglas de mantenimiento

- Las fuentes originales y los acuerdos aprobados prevalecen sobre las síntesis.
- Indicá si un dato es confirmado, propuesto, inferido o pendiente de verificar.
- Al resumir una fuente, enlazala o identificala en `SOURCE_INDEX.md`; no la sustituyas por el resumen.
- Actualizá `CURRENT_STATE.md` al cerrar un cambio que afecte el estado del proyecto. Incluí fecha, cambios, verificaciones realmente realizadas y pendientes relevantes.
- Para cada nueva sesión, contrastá este contexto con el árbol de archivos y el estado actual del repositorio antes de actuar.
- Si una herramienta externa (por ejemplo, un tablero) contiene estado más reciente, registrá el enlace y la fecha de consulta; no supongas que una copia local está sincronizada.
