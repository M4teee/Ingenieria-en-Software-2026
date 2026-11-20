# Informe de QA

Fecha: 20/11/2026.

## Resultado

- `python manage.py check`: correcto, sin problemas.
- `python3.14 scripts/check_docs.py .`: correcto, 42 enlaces Markdown locales.
- `python manage.py test --settings=config.settings_test`: el runner contó 183 elementos y terminó con un error de importación en el módulo raíz `test_demo2_playwright.py` porque el virtualenv no tiene el paquete opcional `playwright`. El resto de la salida no reportó fallos de aserción.
- `python manage.py test main.clienteFinal.tests main.operario.tests.PanelOperarioTests --settings=config.settings_test`: 29 pruebas, todas correctas.

## Verificación visual

No se guardaron screenshots: el servidor Django inició en `127.0.0.1:8000`, pero el navegador automatizado devolvió `Unable to connect` al visitar esa dirección. No se verificaron las resoluciones 1440×900, 1280×800, 768×1024, 390×844 ni 375×812, ni estados hover/focus/error del campo. No se afirma una aprobación visual sin esa evidencia.

## Alcance pendiente

La consola y errores HTTP no pudieron observarse en navegador. Los directorios `artifacts/performance/before/` y `after/` explican por qué no contienen capturas.
