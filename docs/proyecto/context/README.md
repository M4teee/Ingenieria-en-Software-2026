# Fuentes versionadas

Esta carpeta contiene el material usado para comprender el alcance académico del SGR. Los documentos Word son copias de las fuentes recibidas. El [índice de fuentes](../SOURCE_INDEX.md) describe qué aporta cada una y sus límites.

## Exportación de Taiga

El SHA-256 del JSON de entrada queda registrado en `_sanitization.source_sha256` dentro del derivado. El original no se modifica y no se incorpora al repositorio porque contiene datos privados. Para regenerar el derivado a partir de una exportación autorizada:

```sh
python docs/proyecto/context/sanitize_taiga_export.py "/ruta/al/archivo/Historias de Usuario.json" "docs/proyecto/context/Historias de Usuario.sanitized.json"
```

El script informa solo cantidades y no imprime datos de cuenta.

