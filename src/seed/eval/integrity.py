from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path


@dataclass(frozen=True)
class TreeSnapshot:
    root: str
    digest: str
    files: int


def snapshot_tree(root: str | Path) -> TreeSnapshot:
    """Hash a trusted evaluator/control tree in a deterministic path/content order."""
    base = Path(root).resolve()
    if not base.exists() or not base.is_dir():
        raise ValueError(f"Snapshot root is not a directory: {base}")
    digest = hashlib.sha256()
    files = 0
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        rel = path.relative_to(base).as_posix()
        digest.update(rel.encode("utf-8")); digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest()); digest.update(b"\0")
        files += 1
    return TreeSnapshot(str(base), digest.hexdigest(), files)


def unchanged(before: TreeSnapshot, after: TreeSnapshot) -> bool:
    return before.root == after.root and before.digest == after.digest and before.files == after.files
