from __future__ import annotations

from dataclasses import dataclass
import statistics
from typing import Callable, Any

from .suite import EvalSuite, EvalOutcome


@dataclass(frozen=True)
class RepeatedEval:
    candidate_id: str
    runs: int
    mean_score: float
    stdev_score: float
    min_score: float
    max_score: float
    outcomes: tuple[EvalOutcome, ...]


def run_repeated(suite: EvalSuite, candidate_id: str, candidate_factory: Callable[[int], Callable[[str], Any]], *, runs: int = 5) -> RepeatedEval:
    if runs < 2:
        raise ValueError("Repeated evaluation requires at least 2 runs")
    outcomes = tuple(suite.run(f"{candidate_id}:run-{i}", candidate_factory(i)) for i in range(runs))
    scores = [o.score for o in outcomes]
    return RepeatedEval(candidate_id, runs, statistics.fmean(scores), statistics.stdev(scores), min(scores), max(scores), outcomes)
