from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3
from pathlib import Path
from typing import Any

from seed.core.models import utc_now


@dataclass(frozen=True)
class CandidateNode:
    candidate_id: str
    parent_id: str | None
    proposal_id: str
    code_hash: str
    created_at: str


class LineageStore:
    """Durable candidate lineage plus append-only transition/evidence events."""

    def __init__(self, path: str | Path = "seed-lineage.db") -> None:
        self._con = sqlite3.connect(str(path))
        with self._con:
            self._con.execute(
                """CREATE TABLE IF NOT EXISTS candidates (
                candidate_id TEXT PRIMARY KEY,
                parent_id TEXT,
                proposal_id TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
                )"""
            )
            self._con.execute(
                """CREATE TABLE IF NOT EXISTS lineage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id)
                )"""
            )

    def add_candidate(self, candidate_id: str, parent_id: str | None, proposal_id: str, code_hash: str) -> CandidateNode:
        if parent_id is not None and self.get(parent_id) is None:
            raise ValueError("Parent candidate does not exist")
        node = CandidateNode(candidate_id, parent_id, proposal_id, code_hash, utc_now())
        with self._con:
            self._con.execute(
                "INSERT INTO candidates(candidate_id,parent_id,proposal_id,code_hash,created_at) VALUES(?,?,?,?,?)",
                (node.candidate_id, node.parent_id, node.proposal_id, node.code_hash, node.created_at),
            )
        return node

    def record(self, candidate_id: str, kind: str, payload: dict[str, Any]) -> None:
        if self.get(candidate_id) is None:
            raise ValueError("Unknown candidate")
        with self._con:
            self._con.execute(
                "INSERT INTO lineage_events(candidate_id,kind,payload,created_at) VALUES(?,?,?,?)",
                (candidate_id, kind, json.dumps(payload, sort_keys=True), utc_now()),
            )

    def get(self, candidate_id: str) -> CandidateNode | None:
        row = self._con.execute(
            "SELECT candidate_id,parent_id,proposal_id,code_hash,created_at FROM candidates WHERE candidate_id=?", (candidate_id,)
        ).fetchone()
        return CandidateNode(*row) if row else None

    def ancestors(self, candidate_id: str) -> list[CandidateNode]:
        out: list[CandidateNode] = []
        node = self.get(candidate_id)
        while node is not None:
            out.append(node)
            node = self.get(node.parent_id) if node.parent_id else None
        return out
