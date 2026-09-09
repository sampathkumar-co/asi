from __future__ import annotations

import hashlib
import json
from pathlib import Path

_IMPLEMENTATION_DIRS = (
    "src/seed/agent",
    "src/seed/tools",
)
_IMPLEMENTATION_FILES = (
    "src/seed/core/budget.py",
    "src/seed/core/events.py",
    "src/seed/core/models.py",
    "src/seed/providers/base.py",
    "src/seed/providers/budgeted.py",
    "src/seed/providers/ollama.py",
    "src/seed/gate1/local_campaign.py",
)


def implementation_manifest(repo_root: str | Path | None = None) -> dict:
    """Hash the exact Seed implementation used by a local Gate-1 campaign.

    The manifest is based on the actual bytes on disk, not the Git branch name,
    so dirty/local changes cannot silently share a campaign checkpoint.
    """
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[3]
    paths: set[Path] = set()
    for relative in _IMPLEMENTATION_FILES:
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"campaign implementation file missing: {relative}")
        paths.add(path)
    for relative in _IMPLEMENTATION_DIRS:
        directory = root / relative
        if not directory.is_dir():
            raise RuntimeError(f"campaign implementation directory missing: {relative}")
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
