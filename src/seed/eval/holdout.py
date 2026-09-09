from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .cases import EvalCase, exact_match, numeric_match
from .suite import EvalSuite


@dataclass(frozen=True)
class HoldoutManifest:
    suite_id: str
    case_count: int
    sha256: str


def load_private_holdout(path: str | Path, *, repo_root: str | Path | None = None) -> tuple[EvalSuite, HoldoutManifest]:
    """Load a trusted holdout bundle from outside the candidate repository.

    Expected JSON shape:
    {"suite_id":"...","cases":[{"id":"...","prompt":"...","type":"exact|numeric","expected":...}]}
    """
    p = Path(path).resolve()
    if repo_root is not None:
        root = Path(repo_root).resolve()
        if p == root or root in p.parents:
            raise PermissionError("Private holdout must live outside the candidate repository")
    raw = p.read_bytes()
    payload = json.loads(raw)
    cases: list[EvalCase] = []
    for row in payload["cases"]:
        kind = row["type"]
        if kind == "exact":
            scorer = exact_match(str(row["expected"]))
        elif kind == "numeric":
            scorer = numeric_match(float(row["expected"]), float(row.get("tolerance", 1e-9)))
        else:
            raise ValueError(f"Unknown holdout case type: {kind}")
        cases.append(EvalCase(str(row["id"]), str(row["prompt"]), scorer, {"holdout": True}))
    suite = EvalSuite(str(payload["suite_id"]), cases)
    manifest = HoldoutManifest(suite.suite_id, len(cases), hashlib.sha256(raw).hexdigest())
    return suite, manifest
