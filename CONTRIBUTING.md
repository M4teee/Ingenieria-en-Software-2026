# Contribuir

## Entorno

1. Prepará el entorno según la sección [Instalación](README.md#instalación) del README.
2. Creá una rama desde `main` para cada cambio, con el prefijo `feature/`, `fix/` o `docs/` según corresponda.
3. Antes de abrir un pull request, ejecutá la suite completa:

   ```bash
   cd Backend
   python manage.py test --settings=config.settings_test
   ```

## Convenciones

- **Código:** seguí las convenciones del proyecto Django existente (aplicaciones en `Backend/main/`, plantillas en `Backend/templates/`, estilos en `Backend/static/sgr/`). Las pantallas nuevas deben usar los layouts y componentes descritos en [docs/ARQUITECTURA-FRONTEND.md](docs/ARQUITECTURA-FRONTEND.md).
- **Tests:** todo cambio funcional incluye o actualiza pruebas en el `tests.py` de la aplicación correspondiente. Varios tests verifican fragmentos de HTML; si cambiás una plantilla, revisá esa dependencia.
- **Commits:** mensajes descriptivos en castellano.
- **Idioma de la interfaz:** castellano rioplatense, voseo y mayúscula inicial.

## Documentación

Al cambiar código, configuración o dependencias:

1. Contrastá el cambio con [docs/proyecto/CURRENT_STATE.md](docs/proyecto/CURRENT_STATE.md) y actualizalo si cambió lo implementado.
2. Actualizá solo los documentos afectados (README, guía, manual o arquitectura). Registrá en [docs/proyecto/DECISIONS.md](docs/proyecto/DECISIONS.md) únicamente acuerdos confirmados por el equipo.
3. Verificá los enlaces locales:

   ```bash
   python3 scripts/check_docs.py .
   ```

## Seguridad

No incluyas credenciales, claves ni datos personales en el código, los fixtures o la documentación. Las variables sensibles van en `.env` (ver [.env.example](.env.example)), que no se versiona. Para reportar vulnerabilidades, seguí [SECURITY.md](SECURITY.md).
