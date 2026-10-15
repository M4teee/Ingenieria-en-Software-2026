#!/usr/bin/env python3
"""Create a portable Taiga snapshot without account and activity data."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

OMIT_KEYS = {
    "assigned_to", "assigned_users", "attachments", "blocked_code", "blocked_note",
    "email", "history", "invitation_extra_text", "invited_by", "memberships",
    "owner", "timeline", "transfer_token", "user", "user_id", "username",
    "watchers",
}
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def sanitize(value: Any, removed: Counter[str]) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            normalized = key.casefold()
            if normalized in OMIT_KEYS or normalized.endswith("_csv_uuid"):
                removed[normalized] += 1
                continue
            result[key] = sanitize(item, removed)
        return result
    if isinstance(value, list):
        return [sanitize(item, removed) for item in value]
    if isinstance(value, str):
        return EMAIL.sub("[correo omitido]", value)
    return value


def main() -> int:
    if len(sys.argv) != 3:
        print("Uso: python sanitize_taiga_export.py EXPORTACION.json SALIDA.json", file=sys.stderr)
        return 2
    source, destination = (Path(arg).expanduser().resolve() for arg in sys.argv[1:])
    if source == destination or not source.is_file():
        print("La fuente debe existir y ser distinta del destino.", file=sys.stderr)
        return 2
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"No se pudo leer la exportación: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("Se esperaba un objeto JSON de exportación Taiga.", file=sys.stderr)
        return 2

    removed: Counter[str] = Counter()
    clean = sanitize(data, removed)
    clean["_sanitization"] = {
        "source_sha256": digest(source),
        "policy": "Se omitieron propietarios, asignaciones, adjuntos, historial, actividad, watchers y datos de cuentas; correos en texto libre se reemplazaron.",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Exportación derivada creada: {destination.name}; "
        f"épicas={len(clean.get('epics', []))}, "
        f"historias={len(clean.get('user_stories', []))}, "
        f"hitos={len(clean.get('milestones', []))}, "
        f"campos omitidos={sum(removed.values())}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
