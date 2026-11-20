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

- **Código:** seguí las convenciones del proyecto Django existente (aplicaciones en `Backend/main/`, plantillas en `Backend/templates/`, estilos en `Backend/static/sgr/`). Las pantallas nuevas deben usar los layouts y componentes descritos en [docs/arquitectura.md](docs/arquitectura.md#interfaz).
- **Tests:** todo cambio funcional incluye o actualiza pruebas en el `tests.py` de la aplicación correspondiente. Varios tests verifican fragmentos de HTML; si cambiás una plantilla, revisá esa dependencia.
- **Commits:** mensajes descriptivos en castellano.
- **Idioma de la interfaz:** castellano rioplatense, voseo y mayúscula inicial.

## Documentación

Al cambiar código, configuración o dependencias:

1. Actualizá [docs/estado.md](docs/estado.md) si cambió lo implementado, una decisión vigente o una limitación.
2. Actualizá solo los demás documentos afectados (README, instalación, arquitectura o diseño).
3. Verificá los enlaces locales:

   ```bash
   python3 scripts/check_docs.py .
   ```

## Seguridad

No incluyas credenciales, claves ni datos personales en el código, los fixtures o la documentación. Las variables sensibles van en `.env` (ver [.env.example](.env.example)), que no se versiona. Para reportar vulnerabilidades, seguí [SECURITY.md](SECURITY.md).
