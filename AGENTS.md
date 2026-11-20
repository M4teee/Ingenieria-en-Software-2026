# Instrucciones para asistentes de código

Vale para cualquier asistente (Claude, Codex, Copilot u otros). `CLAUDE.md` solo importa este archivo.

## Contexto

- Leé [README.md](README.md), [docs/arquitectura.md](docs/arquitectura.md) y [docs/estado.md](docs/estado.md) antes de cambiar algo. El código prevalece sobre la documentación; si no coinciden, describí la discrepancia.
- Los requisitos originales están en [docs/fuentes/](docs/fuentes/README.md). Son planificación, no evidencia de que algo esté implementado.

## Al cambiar código

- Modificá solo lo que pide la tarea, sin refactors ni renombres ajenos. Preservá los cambios locales y el historial de Git.
- La interfaz usa los layouts y componentes de `Backend/templates/`. Conservá el marcado que exigen los tests (lista en [docs/arquitectura.md](docs/arquitectura.md#marcado-del-que-dependen-los-tests)).
- Ejecutá `python manage.py test --settings=config.settings_test` desde `Backend/` y reportá los resultados reales. No afirmes que algo funciona si no lo verificaste.
- Actualizá `docs/estado.md` y los documentos afectados; verificá enlaces con `python3 scripts/check_docs.py .`.

## Límites

- No hagas commit, push ni despliegues sin una instrucción explícita.
- No registres secretos ni datos personales; las variables sensibles van en `.env`.
- La configuración Django es de desarrollo; no la trates como apta para producción.
