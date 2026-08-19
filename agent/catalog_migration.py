"""Recover the full V0.6 package catalogue from the intact V0.5 source.

This is a one-time-compatible migration helper.  It never executes source code:
only the JSON object and literal .push([...]) package entries are parsed.
"""
from __future__ import annotations

import ast
import json
import os
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = PROJECT_ROOT / "v0.5.html"
TARGET_FILE = PROJECT_ROOT / "frontend" / "packages.json"
BACKUP_FILE = PROJECT_ROOT / "frontend" / "packages.sample-backup.json"


def _balanced_end(source: str, start: int, opening: str, closing: str) -> int:
    """Return the first index after a balanced literal; strings are honoured."""
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("Unclosed data literal in V0.5 source")


def _validate_catalog(catalog: dict[str, list[list[str]]]) -> None:
    if len(catalog) != 16:
        raise ValueError(f"Expected 16 categories, found {len(catalog)}")
    package_total = 0
    for category, packages in catalog.items():
        if not isinstance(category, str) or not category or not isinstance(packages, list):
            raise ValueError("Invalid category data")
        seen: set[str] = set()
        for item in packages:
            if not (isinstance(item, list) and len(item) == 2 and all(isinstance(v, str) and v for v in item)):
                raise ValueError(f"Invalid package entry in {category!r}")
            normalized = item[0].lower()
            if normalized in seen:
                raise ValueError(f"Duplicate package {item[0]!r} in {category!r}")
            seen.add(normalized)
            package_total += 1
    if package_total < 500:
        raise ValueError(f"Catalogue is unexpectedly small ({package_total} packages)")


def build_catalog(source_path: Path = SOURCE_FILE) -> dict[str, list[list[str]]]:
    source = source_path.read_text(encoding="utf-8")
    marker = "const data ="
    marker_at = source.find(marker)
    if marker_at < 0:
        raise ValueError("V0.5 package data declaration was not found")
    object_start = source.find("{", marker_at)
    object_end = _balanced_end(source, object_start, "{", "}")
    catalog: dict[str, list[list[str]]] = json.loads(source[object_start:object_end])

    # V0.5 has post-declaration additions, including the requested 120 packages.
    pattern = re.compile(r"data\[['\"]([^'\"]+)['\"]\]\.push\(")
    cursor = object_end
    while True:
        match = pattern.search(source, cursor)
        if not match:
            break
        args_start = match.end() - 1
        args_end = _balanced_end(source, args_start, "(", ")")
        category = match.group(1)
        entries: Any = ast.literal_eval("[" + source[args_start + 1:args_end - 1] + "]")
        if category not in catalog:
            raise ValueError(f"Unknown appended category: {category}")
        if not all(isinstance(entry, (list, tuple)) and len(entry) == 2 for entry in entries):
            raise ValueError(f"Invalid appended entries for {category}")
        catalog[category].extend([list(entry) for entry in entries])
        cursor = args_end

    _validate_catalog(catalog)
    return catalog


def _read_existing_catalog() -> dict[str, list[list[str]]]:
    """Read and validate the already-migrated catalogue without touching its source."""
    catalog = json.loads(TARGET_FILE.read_text(encoding="utf-8"))
    if not isinstance(catalog, dict):
        raise ValueError("Package catalogue root must be an object")
    _validate_catalog(catalog)
    return catalog


def restore_packages_json(force: bool = False) -> dict[str, int | bool]:
    """Use a valid catalogue, restoring it from V0.5 only when necessary.

    V0.5 is a migration source, not a runtime dependency. This keeps the Agent
    runnable after the legacy source file has been archived or removed.
    """
    if not force and TARGET_FILE.exists():
        try:
            catalog = _read_existing_catalog()
            return {
                "categories": len(catalog),
                "packages": sum(len(items) for items in catalog.values()),
                "restored": False,
            }
        except (OSError, ValueError, json.JSONDecodeError):
            # A missing or invalid target is restored from the legacy source below.
            pass

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Package catalogue is missing or invalid and recovery source was not found: {SOURCE_FILE}"
        )

    catalog = build_catalog()
    total = sum(len(items) for items in catalog.values())
    TARGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    if TARGET_FILE.exists() and not BACKUP_FILE.exists():
        BACKUP_FILE.write_bytes(TARGET_FILE.read_bytes())
    temporary = TARGET_FILE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, TARGET_FILE)
    return {"categories": len(catalog), "packages": total, "restored": True}


if __name__ == "__main__":
    result = restore_packages_json(force=True)
    print(f"Restored {result['packages']} packages in {result['categories']} categories.")
