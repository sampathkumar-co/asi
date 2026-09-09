from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import utc_now


@dataclass(frozen=True)
class MemoryItem:
    run_id: str
    kind: str
    content: str
    tags: tuple[str, ...]
    metadata: dict[str, Any]
    created_at: str


class MemoryStore:
    """Persistent append-only working/research memory with simple tagged retrieval."""

    def __init__(self, path: str | Path = "seed-memory.db") -> None:
        self._con = sqlite3.connect(str(path))
        with self._con:
            self._con.execute(
                """CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL
                )"""
            )
            self._con.execute("CREATE INDEX IF NOT EXISTS idx_memory_run ON memory(run_id, id)")

    def append(self, run_id: str, kind: str, content: str, *, tags: tuple[str, ...] = (), metadata: dict[str, Any] | None = None) -> MemoryItem:
        item = MemoryItem(run_id, kind, content, tuple(tags), metadata or {}, utc_now())
        with self._con:
            self._con.execute(
                "INSERT INTO memory(run_id, kind, content, tags, metadata, created_at) VALUES(?,?,?,?,?,?)",
                (item.run_id, item.kind, item.content, json.dumps(item.tags), json.dumps(item.metadata, sort_keys=True), item.created_at),
            )
        return item

    def recent(self, run_id: str, *, limit: int = 20, kind: str | None = None) -> list[MemoryItem]:
        if limit < 1:
            return []
        if kind:
            rows = self._con.execute(
                "SELECT run_id,kind,content,tags,metadata,created_at FROM memory WHERE run_id=? AND kind=? ORDER BY id DESC LIMIT ?",
                (run_id, kind, limit),
            ).fetchall()
        else:
            rows = self._con.execute(
                "SELECT run_id,kind,content,tags,metadata,created_at FROM memory WHERE run_id=? ORDER BY id DESC LIMIT ?",
                (run_id, limit),
            ).fetchall()
        rows.reverse()
        return [MemoryItem(r[0], r[1], r[2], tuple(json.loads(r[3])), json.loads(r[4]), r[5]) for r in rows]

    def close(self) -> None:
        self._con.close()
