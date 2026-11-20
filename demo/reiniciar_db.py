#!/usr/bin/env python
"""Vacía la base de datos local de Django y carga los datos de demostración.

Atención: `flush` borra todos los datos de la base configurada.
"""

from pathlib import Path
import subprocess
import sys


def main() -> None:
    raiz = Path(__file__).resolve().parent.parent
    backend = raiz / "Backend"
    manage_py = backend / "manage.py"
    fixture = Path(__file__).resolve().parent / "datos-demo.json"

    # --noinput evita la confirmación interactiva de flush.
    subprocess.run(
        [sys.executable, str(manage_py), "flush", "--noinput"],
        cwd=backend,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(manage_py), "loaddata", str(fixture)],
        cwd=backend,
        check=True,
    )


if __name__ == "__main__":
    main()
