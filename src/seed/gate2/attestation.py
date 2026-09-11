from __future__ import annotations

import hashlib
import json
from pathlib import Path

_IMPLEMENTATION_DIRS = (
    "src/seed/gate2",
    "src/seed/science",
)
_IMPLEMENTATION_FILES = (
    "src/seed/core/budget.py",
    "src/seed/providers/base.py",
    "src/seed/providers/budgeted.py",
    "src/seed/providers/ollama.py",
)


def implementation_manifest(repo_root: str | Path | None = None) -> dict:
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[3]
    paths: set[Path] = set()
    for relative in _IMPLEMENTATION_FILES:
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"Gate-2 implementation file missing: {relative}")
        paths.add(path)
    for relative in _IMPLEMENTATION_DIRS:
        directory = root / relative
        if not directory.is_dir():
            raise RuntimeError(f"Gate-2 implementation directory missing: {relative}")
        paths.update(path for path in directory.rglob("*.py") if path.is_file())

    files = []
    for path in sorted(paths, key=lambda p: p.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        files.append({
            "path": relative,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    encoded = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return {
        "digest": hashlib.sha256(encoded).hexdigest(),
        "file_count": len(files),
        "files": files,
    }
