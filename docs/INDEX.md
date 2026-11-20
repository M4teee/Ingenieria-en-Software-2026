# Documentación

## Uso y desarrollo

| Documento | Contenido |
|---|---|
| [GUIA-EJECUCION-Y-PRUEBAS.md](GUIA-EJECUCION-Y-PRUEBAS.md) | Instalación, elección de base de datos (SQLite o PostgreSQL/Neon), pruebas automatizadas y errores frecuentes. |
| [MANUAL-DE-USO.md](MANUAL-DE-USO.md) | Procedimientos para cliente, operario, repartidor y administrador. |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Módulos Django, recorrido de un pedido, modelo de datos y accesos por rol. |
| [ARQUITECTURA-FRONTEND.md](ARQUITECTURA-FRONTEND.md) | Plantillas, layouts, componentes, Basecoat UI y dependencias de los tests sobre el HTML. |
| [SISTEMA-DE-DISENO.md](SISTEMA-DE-DISENO.md) | Identidad visual: paleta, tipografía, composición por rol y movimiento. |
| [../demo/README.md](../demo/README.md) | Datos de demostración y credenciales de prueba. |

## Registro del proyecto

Material del proceso académico (Ingeniería de Software 2026): requisitos, decisiones y estado verificado. Las fuentes originales prevalecen sobre sus resúmenes.

| Documento | Contenido |
|---|---|
| [proyecto/PROJECT_BRIEF.md](proyecto/PROJECT_BRIEF.md) | Propósito, alcance y requisitos extraídos de las fuentes. |
| [proyecto/SOURCE_INDEX.md](proyecto/SOURCE_INDEX.md) | Fuentes académicas originales (entrevistas, requisitos, PGP, backlog) y sus límites. |
| [proyecto/context/](proyecto/context/README.md) | Copias de las fuentes y exportación sanitizada del backlog de Taiga. |
| [proyecto/KNOWLEDGE_BASE.md](proyecto/KNOWLEDGE_BASE.md) | Síntesis de contexto y discrepancias entre fuentes. |
| [proyecto/DECISIONS.md](proyecto/DECISIONS.md) | Decisiones técnicas registradas y temas sin resolver. |
| [proyecto/CURRENT_STATE.md](proyecto/CURRENT_STATE.md) | Implementación observada, verificaciones ejecutadas y pendientes, por fecha. |
| [proyecto/INFORME-AUDITORIA-PRE-DEMO-2026-11-19.md](proyecto/INFORME-AUDITORIA-PRE-DEMO-2026-11-19.md) | Trazabilidad de las 31 historias de usuario y resultados de la auditoría previa a la demo. |

## Mantenimiento

- Al cambiar código o configuración, actualizá `proyecto/CURRENT_STATE.md` y solo los documentos afectados (ver [CONTRIBUTING.md](../CONTRIBUTING.md)).
- Registrá en `proyecto/DECISIONS.md` solo acuerdos confirmados; las alternativas abiertas quedan como pendientes.
- Anotá únicamente verificaciones ejecutadas y el entorno en que se hicieron.
- `python3 scripts/check_docs.py .` comprueba enlaces locales y rutas propias de una máquina; no valida la exactitud funcional.
