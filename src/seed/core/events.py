from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import utc_now


@dataclass(frozen=True)
class Event:
    run_id: str
    kind: str
    payload: dict[str, Any]
    created_at: str
    prev_hash: str
    event_hash: str


class EventStore:
    """Append-only SQLite event store with a per-run SHA-256 hash chain.

    The store owns one SQLite connection for its lifetime. Use it as a context
    manager (preferred) or call ``close()`` explicitly so Windows can release
    the database file immediately.
    """

    def __init__(self, path: str | Path = "seed.db") -> None:
        self.path = str(path)
        self._con: sqlite3.Connection | None = sqlite3.connect(self.path)
        self._init_db()

    def __enter__(self) -> "EventStore":
        if self._con is None:
            raise RuntimeError("EventStore is closed")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _connect(self) -> sqlite3.Connection:
        if self._con is None:
            raise RuntimeError("EventStore is closed")
        return self._con

    def close(self) -> None:
        if self._con is not None:
            self._con.close()
            self._con = None

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL UNIQUE
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_events_run_id ON events(run_id, id)")

    @staticmethod
    def _digest(run_id: str, kind: str, payload: dict[str, Any], created_at: str, prev_hash: str) -> str:
        body = json.dumps(
            {
                "run_id": run_id,
                "kind": kind,
                "payload": payload,
                "created_at": created_at,
                "prev_hash": prev_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(body).hexdigest()

    def append(self, run_id: str, kind: str, payload: dict[str, Any]) -> Event:
        with self._connect() as con:
            row = con.execute(
                "SELECT event_hash FROM events WHERE run_id=? ORDER BY id DESC LIMIT 1", (run_id,)
            ).fetchone()
            prev_hash = row[0] if row else "GENESIS"
            created_at = utc_now()
            event_hash = self._digest(run_id, kind, payload, created_at, prev_hash)
            con.execute(
                "INSERT INTO events(run_id, kind, payload, created_at, prev_hash, event_hash) VALUES(?,?,?,?,?,?)",
                (run_id, kind, json.dumps(payload, sort_keys=True), created_at, prev_hash, event_hash),
            )
        return Event(run_id, kind, payload, created_at, prev_hash, event_hash)

    def list(self, run_id: str) -> list[Event]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT run_id, kind, payload, created_at, prev_hash, event_hash FROM events WHERE run_id=? ORDER BY id",
                (run_id,),
            ).fetchall()
        return [Event(r[0], r[1], json.loads(r[2]), r[3], r[4], r[5]) for r in rows]

    def verify_chain(self, run_id: str) -> bool:
        prev = "GENESIS"
        for event in self.list(run_id):
            if event.prev_hash != prev:
                return False
            expected = self._digest(event.run_id, event.kind, event.payload, event.created_at, event.prev_hash)
            if expected != event.event_hash:
                return False
            prev = event.event_hash
        return True
