#!/usr/bin/env python3
"""Check local Markdown links and flag machine-specific paths."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((<[^>]+>|[^)]+)\)")
LOCAL_PATH_RE = re.compile(
    r"(?<!\S)(?:~[/\\]|/(?:Users|home|private|tmp)/|[A-Za-z]:\\Users\\)\S*"
)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "build", "dist", "__pycache__"}


def markdown_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*.md")
        if not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
    )


def check_documentation(folder: Path) -> tuple[list[str], list[str], int]:
    root = folder.resolve()
    if not root.is_dir():
        raise ValueError(f"No es una carpeta: {folder}")

    missing: list[str] = []
    nonportable: list[str] = []
    checked_links = 0
    for markdown in markdown_files(root):
        relative = markdown.relative_to(root)
        content = markdown.read_text(encoding="utf-8")
        content = re.sub(r"```.*?```|~~~.*?~~~", "", content, flags=re.DOTALL)

        for match in LOCAL_PATH_RE.finditer(content):
            nonportable.append(f"{relative}: {match.group(0)}")

        for match in LINK_RE.finditer(content):
            target = match.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            target = unquote(target.split("#", 1)[0].split("?", 1)[0].strip())
            if not target:
                continue
            parts = urlsplit(target)
            if parts.scheme or parts.netloc:
                if parts.scheme == "file":
                    nonportable.append(f"{relative}: {target}")
                continue
            if target.startswith(("/", "~/")) or re.match(r"^[A-Za-z]:[\\/]", target):
                nonportable.append(f"{relative}: {target}")
                continue

            checked_links += 1
            linked_path = (markdown.parent / target).resolve()
            try:
                linked_path.relative_to(root)
            except ValueError:
                missing.append(f"{relative}: la ruta sale del repositorio ({target})")
                continue
            if not linked_path.exists():
                missing.append(f"{relative}: no existe {target}")

    return missing, sorted(set(nonportable)), checked_links


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="project-init docs-check",
        description="Comprueba enlaces Markdown locales y señala rutas dependientes del equipo.",
    )
    parser.add_argument("path", nargs="?", default=".", help="raíz del proyecto")
    args = parser.parse_args(argv)
    try:
        missing, nonportable, checked = check_documentation(Path(args.path))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for item in missing:
        print(f"ERROR: enlace local inválido: {item}")
    for item in nonportable:
        print(f"AVISO: ruta local que puede no funcionar en otro clon: {item}")
    if not missing:
        print(f"OK: {checked} enlaces Markdown locales verificados.")
    if nonportable:
        print(f"Revisión manual: {len(nonportable)} referencia(s) a rutas locales.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
