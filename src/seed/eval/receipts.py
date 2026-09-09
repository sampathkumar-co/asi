from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
from typing import Any

from seed.core.models import utc_now


@dataclass(frozen=True)
class EvalReceipt:
    suite_id: str
    candidate_id: str
    score: float
    case_scores: dict[str, float]
    metrics: dict[str, Any]
    created_at: str
    content_hash: str


def make_receipt(suite_id: str, candidate_id: str, score: float, case_scores: dict[str, float], metrics: dict[str, Any]) -> EvalReceipt:
    created_at = utc_now()
    body = {
        "suite_id": suite_id,
        "candidate_id": candidate_id,
        "score": score,
        "case_scores": case_scores,
        "metrics": metrics,
        "created_at": created_at,
    }
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return EvalReceipt(**body, content_hash=digest)


def write_receipt(receipt: EvalReceipt, path: str | Path) -> None:
    Path(path).write_text(json.dumps(asdict(receipt), indent=2, sort_keys=True), encoding="utf-8")
