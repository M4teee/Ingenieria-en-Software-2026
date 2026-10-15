# Fuentes versionadas

Esta carpeta contiene el material usado para comprender el alcance académico del SGR. Los documentos Word son copias byte por byte de las fuentes recibidas. El [índice de fuentes](../SOURCE_INDEX.md) describe qué aporta cada una y sus límites.

## Exportación de Taiga

El archivo completo recibido era una exportación de un proyecto marcado como privado. Incluía datos de cuentas y 318 eventos de actividad que no son necesarios para comprender los requisitos del producto. Por eso el repositorio contiene `Historias de Usuario.sanitized.json`, una derivación reproducible que conserva la configuración funcional del tablero, las épicas, las historias, los hitos y sus campos de estado, pero omite cuentas, asignaciones, watchers, adjuntos, notas de bloqueo e historial/actividad. También reemplaza direcciones de correo que aparezcan dentro de texto libre.

El SHA-256 del JSON de entrada queda registrado en `_sanitization.source_sha256` dentro del derivado. El original no se modifica y no se incorpora al repositorio. Para regenerar el derivado a partir de una exportación autorizada:

```sh
python docs/context/sanitize_taiga_export.py "/ruta/al/archivo/Historias de Usuario.json" "docs/context/Historias de Usuario.sanitized.json"
```

El script informa solo cantidades, no imprime datos de cuenta. La derivación sigue siendo una fuente secundaria: una historia registrada no prueba que esté implementada ni que su estado siga vigente. Esta carpeta no contiene credenciales ni ofrece conexión a Taiga.

## Uso y redistribución

No se encontró una licencia o prohibición explícita de redistribución dentro de los cinco documentos Word inspeccionados. Eso no determina sus derechos de publicación. Los documentos académicos contienen nombres de participantes y el PGP incluye un dato de contacto; los originales se mantuvieron intactos y no se reprodujeron esos datos en los índices. Antes de hacer público el repositorio, el equipo debe confirmar que puede compartir el material y que esos datos siguen siendo necesarios. El PGP menciona IEEE Std 1058, pero no reproduce el estándar.
