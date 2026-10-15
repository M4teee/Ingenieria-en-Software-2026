# Fuentes versionadas

Esta carpeta contiene el material usado para comprender el alcance académico del SGR. Los documentos Word son copias de las fuentes recibidas. El [índice de fuentes](../SOURCE_INDEX.md) describe qué aporta cada una y sus límites.

## Exportación de Taiga

El SHA-256 del JSON de entrada queda registrado en `_sanitization.source_sha256` dentro del derivado. El original no se modifica y no se incorpora al repositorio (tiene datos privados lol). Para regenerar el derivado a partir de una exportación autorizada:

```sh
python docs/context/sanitize_taiga_export.py "/ruta/al/archivo/Historias de Usuario.json" "docs/context/Historias de Usuario.sanitized.json"
```

Este script "sanitiza" una exportacion de Tiga (informa solo cantidades, no imprime datos de cuenta), lo dejo por si lo necesitamos usar de nuevo.

