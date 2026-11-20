# Política de seguridad

## Alcance de la configuración actual

`Backend/config/settings.py` es una configuración de **desarrollo** y no está preparada para producción:

- `DEBUG = True` y `ALLOWED_HOSTS` vacío.
- Si no se define `DJANGO_SECRET_KEY`, se usa una clave de desarrollo pública.
- El ingreso por PIN de 4 dígitos no limita la cantidad de intentos.
- No hay configuración de HTTPS, cookies seguras ni encabezados HSTS.
- Los PIN se guardan como texto para que el operario pueda comunicarlos (decisión registrada en [docs/proyecto/DECISIONS.md](docs/proyecto/DECISIONS.md)).

## Antes de desplegar

1. Definí `DJANGO_SECRET_KEY` con un valor aleatorio propio (ver [.env.example](.env.example)).
2. Desactivá `DEBUG` y configurá `ALLOWED_HOSTS`.
3. Serví la aplicación detrás de HTTPS y activá `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` y HSTS.
4. Limitá los intentos de ingreso por PIN.
5. Ejecutá `python manage.py check --deploy` y revisá la [lista de verificación de despliegue de Django](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/).

## Reportar una vulnerabilidad

No abras un issue público con los detalles. Si el repositorio tiene habilitado el reporte privado de vulnerabilidades, usá **Report a vulnerability** en la pestaña *Security* de GitHub; si no, escribí en privado a los mantenedores. Incluí los pasos para reproducirla y el impacto que observaste.
