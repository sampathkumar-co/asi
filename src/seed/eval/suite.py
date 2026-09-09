from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable

from .cases import EvalCase
from .metrics import RunMetrics
from .receipts import EvalReceipt, make_receipt


CandidateFn = Callable[[str], Any]


@dataclass(frozen=True)
class EvalOutcome:
    score: float
    case_scores: dict[str, float]
    metrics: RunMetrics
    receipt: EvalReceipt


class EvalSuite:
    def __init__(self, suite_id: str, cases: list[EvalCase]) -> None:
        if not cases:
            raise ValueError("EvalSuite requires at least one case")
        ids = [c.case_id for c in cases]
        if len(ids) != len(set(ids)):
            raise ValueError("Eval case IDs must be unique")
        self.suite_id = suite_id
        self.cases = list(cases)

    def run(self, candidate_id: str, candidate: CandidateFn) -> EvalOutcome:
        started = time.perf_counter()
        scores: dict[str, float] = {}
        for case in self.cases:
            try:
                output = candidate(case.prompt)
                raw = float(case.scorer(output))
                score = min(1.0, max(0.0, raw))
            except Exception:
                score = 0.0
            scores[case.case_id] = score
        wall = time.perf_counter() - started
        total = sum(scores.values()) / len(scores)
        metrics = RunMetrics(capability_score=total, cases=len(scores), wall_time_s=wall)
        receipt = make_receipt(self.suite_id, candidate_id, total, scores, {"wall_time_s": wall, "cases": len(scores)})
        return EvalOutcome(total, scores, metrics, receipt)
